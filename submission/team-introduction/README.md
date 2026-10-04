# 团队介绍视频

成片：`team-introduction.mp4`，约 20 秒，1920×1080、30 fps，H.264 视频和 AAC 音频，约 1.7 MB。

内容：Ruihua He 以 whardite 队唯一参赛者身份介绍 Rental Housing Law Navigator，以及设计、开发和测试职责。三个文字画面配轻微入场动画，英文旁白和字幕，无真人出镜。

- 配音：ElevenLabs，Roger - Laid-Back, Casual, Resonant，Eleven v4。
- 原始录音：`assets/elevenlabs-narration.mp3`，17.240813 秒；在视频的 0.6 秒处开始，完整播放。
- 旁白稿：`narration.txt`；字幕：`captions.json` 和 `team-introduction.srt`。
- 制作工程：`remotion/`，Remotion 4.0.532。
- 配音来源截图：`assets/elevenlabs-proof.jpg`；制作信息：`assets/provenance.json`。

## 修改和导出

```sh
cd remotion
npm ci
npx remotion studio --no-open
```

打开控制台显示的网址，选择 `TeamIntro`。三个场景也可在 `Scenes` 文件夹中单独编辑。

```sh
npm run lint
npx remotion render TeamIntro ../team-introduction.mp4 --codec=h264 --crf=18 --pixel-format=yuv420p
```

画面使用系统 Arial / Helvetica 字体。字幕直接写在 `src/Composition.tsx` 中，便于在 Remotion 中编辑。`src/basic-captions.tsx` 采用 Remotion 官方 Basic Captions 原始组件。

## 已做检查

- TypeScript 和 ESLint 检查通过。
- 查看三个场景的导出画面，确认文字完整、没有重叠和超出边缘。
- 使用 Remotion 的本地 Whisper 转写配音，按实际发音时间调整字幕；人名、队名按旁白稿保留正确拼写。
- 最终 MP4 可完整解码；画面 20 秒，含音频的容器总时长 20.011 秒，文件大小 1,704,973 字节。
- 本视频只制作团队介绍，尚未上传比赛页面。
