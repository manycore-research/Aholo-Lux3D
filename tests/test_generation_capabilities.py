"""Offline checks against the maintained installation input, never a release ZIP."""
import importlib.util
import json
from pathlib import Path
import sys
import unittest
from unittest import mock

SKILL = Path(__file__).resolve().parents[1] / 'plugins/common/aholo-lux3d'
RUNTIME = SKILL / 'core/runtime'
sys.path.insert(0, str(RUNTIME))
spec = importlib.util.spec_from_file_location('public_generation_client', RUNTIME / 'lux3d_client.py')
client = importlib.util.module_from_spec(spec)
spec.loader.exec_module(client)
MODEL = 'https://example.com/model.glb'
QUOTE = 'quote_' + 'a' * 32


class GenerationCapabilitiesTests(unittest.TestCase):
    def test_four_creates_use_canonical_regional_paths_and_matching_quote_trace(self):
        calls = [
            ('mesh-retopology', client.create_mesh_retopology_task, (MODEL, 10000), {'content_id': QUOTE}),
            ('articulation-animation', client.create_articulation_animation_task, (MODEL, 'Open the lid'), {}),
            ('auto-rig', client.create_auto_rig_task, (MODEL,), {'content_id': QUOTE}),
            ('animation-retarget', client.create_animation_retarget_task,
             (MODEL, ['Dance_Loop', 'Walk_Loop']), {'content_id': QUOTE}),
        ]
        contract = json.loads((SKILL / 'core/contracts/lux3d-generation.v1.json').read_text(encoding='utf-8'))
        for region, base in [('cn', 'https://api.aholo3d.cn'), ('international', 'https://api.aholo.ai/global')]:
            for name, create, args, kwargs in calls:
                with self.subTest(region=region, operation=name):
                    response = mock.Mock(status_code=200)
                    response.json.return_value = {'f': None, 'c': '0', 'm': '', 'd': 9223372036854775807}
                    with mock.patch.object(client.requests, 'request', return_value=response) as http:
                        task_id = create(*args, region=region, api_key='offline-fixture-key', **kwargs)
                    self.assertEqual(task_id, '9223372036854775807')
                    http.assert_called_once()
                    self.assertEqual(http.call_args.kwargs['url'], base + contract['endpoints'][name]['path'])
                    body = http.call_args.kwargs['json']
                    if name == 'articulation-animation':
                        self.assertEqual(set(body), {'glbUrl', 'prompt'})
                    else:
                        self.assertEqual(body['contentId'], QUOTE)

    def test_invalid_actions_fail_before_any_create_request(self):
        for actions in [[], ['Dance_Loop'] * 2, ['not-a-public-action'], ['Dance_Loop'] * 11]:
            with self.subTest(actions=actions), mock.patch.object(client.requests, 'request') as http:
                with self.assertRaises(ValueError):
                    client.create_animation_retarget_task(MODEL, actions, region='cn', api_key='offline-fixture-key')
                http.assert_not_called()

    def test_empty_optional_texture_zip_is_not_a_retopology_failure(self):
        artifacts = client.parse_mesh_retopology_output({'outputs': [
            {'content': 'https://example.com/model.glb'},
            {'content': 'https://example.com/model.obj'}, {'content': ''}]})
        self.assertEqual(set(artifacts), {'glb', 'obj'})
        result = client.retopology_result('123', artifacts, True)
        self.assertFalse(result['texturePackageAvailable'])
        self.assertEqual(result['warnings'], ['TEXTURE_PACKAGE_NOT_GENERATED'])

    def test_provider_success_preserves_per_action_failure_for_retargeting(self):
        actions = {'actions': [
            {'animation_id': 'Dance_Loop', 'status': 'success', 'animationGlbUrl': 'https://example.com/dance.glb'},
            {'animation_id': 'Walk_Loop', 'status': 'failed', 'error': {'code': 'ACTION_FAILED'}},
        ]}
        with mock.patch.object(client, 'get_task', return_value={
                'status': 3, 'outputs': [{'content': json.dumps(actions)}]}):
            result = client.query_task_status('123', region='cn', max_attempts=1, interval=0)
        self.assertEqual(result, actions)

    def test_articulation_keeps_the_actual_result_format(self):
        for suffix in ['.glb', '.fbx', '.zip']:
            url = 'https://example.com/model' + suffix + '?signature=opaque'
            self.assertEqual(client.parse_articulation_animation_output({'outputs': [{'content': url}]}), url)
            self.assertEqual(client.articulation_result_extension(url), suffix)
        with self.assertRaises(ValueError):
            client.parse_articulation_animation_output({'outputs': []})


if __name__ == '__main__':
    unittest.main()
