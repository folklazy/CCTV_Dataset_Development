"""Independent tiny fixtures for native projections and the B5 extension."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

import numpy as np
from PIL import Image
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import evaluate_helper_zero_shot as zero
import train_annotation_helper as trainer
import report_helper_comparison as reporter


class ZeroShotRequirements(unittest.TestCase):
    def test_complete_mappings_and_supported_classes(self):
        protocol = json.loads((ROOT/'config/helper_zero_shot_v1.json').read_text())
        for model, count in [('b4',18), ('b5',18), ('solider',20)]:
            contract = protocol['models'][model]
            self.assertEqual(len(contract['native_labels']), count)
            self.assertEqual(len(contract['target_map']), count)
            native = np.arange(count, dtype=np.uint8)[None]
            mapped = zero.project_native(native, contract['target_map'])
            self.assertEqual(set(mapped.flatten()), {0,1,2,3,4})
            self.assertEqual(int(mapped[0,2]),1)
        self.assertEqual(protocol['models']['b5']['target_map'][11],2)
        self.assertEqual(protocol['models']['solider']['target_map'][13],2)
        self.assertEqual(protocol['models']['solider']['target_map'][6],0)

    def test_invalid_prediction_ids_fail(self):
        for native in [np.array([[255]]), np.array([[-1]]), np.array([[1.5]])]:
            with self.assertRaises(ValueError):
                zero.project_native(native, [0,1,2,3,4])

    def test_fashn_rgb_channel_order(self):
        image = Image.new('RGB',(11,17),(255,127,0))
        value = zero.native_fashn_input(image)
        expected = (torch.tensor([1.,127/255,0.])-torch.tensor([.485,.456,.406]))/torch.tensor([.229,.224,.225])
        torch.testing.assert_close(value[0,:,300,100],expected)
        self.assertEqual(value.shape,(1,3,576,384))

    def test_native_probability_composition(self):
        probabilities = torch.tensor([[[.8,.4]],[[.7,.9]]])
        scores = torch.tensor([.2,.8])
        torch.testing.assert_close(zero.query_plane(probabilities,scores),torch.tensor([[.56,.72]]))
        torch.testing.assert_close(zero.query_plane(torch.empty(0,2,3),torch.empty(0)),torch.zeros(2,3))

    def test_union_and_other_false_positive_false_negative(self):
        protocol=json.loads((ROOT/'config/helper_zero_shot_v1.json').read_text())
        pred=zero.project_native(np.array([[6,6]]),protocol['models']['b5']['target_map'])
        self.assertEqual(pred.tolist(),[[4,4]])
        cm=np.zeros((5,5),dtype=np.int64)
        cm[4,4]=2
        self.assertEqual(trainer.metrics_from_confusion(cm,1)['per_class_iou']['lower'],1.)
        cm=np.zeros((5,5),dtype=np.int64)
        cm[3,0]=1
        cm[0,3]=1
        result=trainer.metrics_from_confusion(cm,1)
        self.assertEqual(result['per_class_statistics']['upper']['fp'],1)
        self.assertEqual(result['per_class_statistics']['upper']['fn'],1)
        self.assertEqual(result['per_class_iou']['upper'],0.)

    def test_b5_head_initialization_is_separate_from_native_head(self):
        native=torch.nn.Conv2d(2,18,1)
        with torch.no_grad():
            for label in range(18):
                native.weight[label].fill_(label)
                native.bias[label]=label
        labels={i:f'class{i}' for i in range(18)}
        labels.update({0:'Background',2:'Hair',4:'Upper-clothes',5:'Skirt',6:'Pants',11:'Face'})
        model=SimpleNamespace(config=SimpleNamespace(num_labels=18,depths=[3,6,40,3],id2label=labels),
                              decode_head=SimpleNamespace(classifier=native))
        trainer.initialize_b5_classifier(model)
        self.assertEqual(model.decode_head.classifier.weight[:,0,0,0].tolist(),[0,2,11,4,5.5])
        self.assertEqual(native.out_channels,18)
        self.assertEqual(model.config.id2label,dict(enumerate(trainer.CLASSES)))

    def test_b5_image_resize_preserves_target_grid(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            Image.new('RGB',(384,576),(20,80,170)).save(root/'image.png')
            Image.new('L',(384,576),3).save(root/'mask.png')
            hashes={p.name:trainer.file_hash(p) for p in root.iterdir()}
            items=[{'img_path':'image.png','mask_path':'mask.png'}]
            image,target,_=trainer.Crops(root,items,hashes,image_size=(512,512))[0]
            self.assertEqual(image.shape,(3,512,512))
            self.assertEqual(target.shape,(576,384))
            self.assertTrue(torch.all(target==3))

    def test_report_preserves_missing_values_and_stage_separation(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            data=root/'data'
            data.mkdir()
            items=[]
            for idx in range(3):
                Image.new('RGB',(2,2),(40,80,120)).save(data/f'{idx}.png')
                Image.new('L',(2,2),1).save(data/f'{idx}_gt.png')
                items.append({'sample_id':str(idx),'img_path':f'{idx}.png','mask_path':f'{idx}_gt.png'})
            (data/'MANIFEST.json').write_text(json.dumps({'val':items}))
            out=root/'zero'
            out.mkdir()
            predictions=out/'validation_predictions'
            predictions.mkdir()
            for idx in range(3):Image.new('L',(2,2),1).save(predictions/f'{idx}.png')
            confusion=[[0]*5 for _ in range(5)]
            confusion[1][1]=12
            metrics={'crop_count':3,'per_class_iou':{},'per_class_statistics':{},'miou4':1.,'confusion':confusion}
            for label in ['hair','face','upper','lower']:
                metrics['per_class_iou'][label]=1. if label=='hair' else None
                metrics['per_class_statistics'][label]=dict.fromkeys(['precision','recall','f1_dice'],1. if label=='hair' else None)
                metrics['per_class_statistics'][label].update(dict.fromkeys(['gt_pixels','prediction_pixels','union'],12 if label=='hair' else 0))
            (out/'METRICS.json').write_text(json.dumps(metrics))
            checkpoint=root/'BEST.pt'
            checkpoint.write_bytes(b'fixture checkpoint')
            (out/'STATUS.json').write_text(json.dumps({'state':'COMPLETE','checkpoint':str(checkpoint),'checkpoint_sha256':hashlib.sha256(checkpoint.read_bytes()).hexdigest()}))
            binding={'dataset':{'manifest_sha256':hashlib.sha256((data/'MANIFEST.json').read_bytes()).hexdigest(),
                                'files':{item['mask_path']:hashlib.sha256((data/item['mask_path']).read_bytes()).hexdigest() for item in items}},'protocol_sha256':'fixture','weights_role':'PRETRAINED_NO_CCTV_FINETUNING'}
            (out/'BINDING.json').write_text(json.dumps(binding))
            config={'dataset':str(data),'zero_shot_protocol_sha256':'fixture','comparison_entries':[
                {'key':'B4','stage':'ZERO_SHOT','output':str(out),'mask_folder':'validation_predictions','verify_saved_masks':True},
                {'key':'B5','stage':'FINE_TUNED','output':str(root/'not_started'),'mask_folder':'validation_predictions'}]}
            path=root/'manifest.json'
            path.write_text(json.dumps(config))
            with mock.patch.object(sys,'argv',['report',str(path)]):reporter.main()
            result=json.loads((root/'RESULT_INDEX.json').read_text())
            self.assertEqual(result['state'],'PARTIAL')
            self.assertIsNone(result['rows'][1]['miou4'])
            self.assertEqual(len(list((root/'gallery').glob('*.png'))),6)
            self.assertEqual(json.loads((out/'SAVED_MASK_AUDIT.json').read_text())['exact_ids'],3)
            Image.new('L',(2,2),0).save(predictions/'0.png')
            with mock.patch.object(sys,'argv',['report',str(path)]), self.assertRaisesRegex(ValueError,'confusion mismatch'):
                reporter.main()


if __name__=='__main__':unittest.main()
