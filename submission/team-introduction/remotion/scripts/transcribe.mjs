import {registerMediabunnyServer} from '@mediabunny/server';
import {canUseWhisperWebGpu, downloadWhisperModel, loadWhisperModel, transcribe, toCaptions} from '@remotion/whisper-webgpu';
import {readFile, writeFile} from 'node:fs/promises';
import {execFileSync} from 'node:child_process';

registerMediabunnyServer();
const support = await canUseWhisperWebGpu();
if (!support.supported) throw new Error(support.detailedReason);
execFileSync('ffmpeg', ['-y', '-v', 'error', '-i', 'public/narration.mp3', '-ar', '16000', '-ac', '1', '-f', 'f32le', '../assets/narration-16k.f32']);
const data = await readFile('../assets/narration-16k.f32');
const channelWaveform = new Float32Array(data.buffer.slice(data.byteOffset, data.byteOffset + data.byteLength));
const model = 'small.en';
await downloadWhisperModel({model});
const handle = await loadWhisperModel({model});
try {
  const transcription = await transcribe({channelWaveform, model});
  const {captions} = toCaptions({whisperWebGpuOutput: transcription});
  await writeFile('../assets/transcription.json', JSON.stringify(transcription, null, 2));
  await writeFile('../assets/captions-transcribed.json', JSON.stringify(captions, null, 2));
  console.log(captions);
} finally {
  await handle[Symbol.asyncDispose]();
}
