import { Audio } from "@remotion/media";
import {
  AbsoluteFill,
  Composition,
  Interactive,
  Sequence,
  staticFile,
} from "remotion";
import { OpeningScene } from "./OpeningScene";
import { ProjectScene } from "./ProjectScene";
import { FocusScene } from "./FocusScene";
import { BasicCaptions } from "./basic-captions";

export const TeamIntro: React.FC = () => (
  <AbsoluteFill
    style={{
      backgroundColor: "#142820",
      fontFamily: "Arial, Helvetica, sans-serif",
    }}
  >
    <Interactive.Div
      name="Top rule"
      style={{
        position: "absolute",
        top: 180,
        left: 144,
        right: 144,
        height: 2,
        backgroundColor: "#345044",
      }}
    />
    <Interactive.Div
      name="Team wordmark"
      style={{
        position: "absolute",
        top: 93,
        left: 144,
        fontSize: 52,
        lineHeight: 1,
        fontWeight: 700,
        letterSpacing: -1.6,
        color: "#F5F2EA",
      }}
    >
      whardite
    </Interactive.Div>
    <Interactive.Div
      name="Event label"
      style={{
        position: "absolute",
        top: 101,
        right: 144,
        fontSize: 31,
        letterSpacing: 3,
        color: "#A8CFB9",
      }}
    >
      HACK-NATION · TEAM INTRODUCTION
    </Interactive.Div>
    <Sequence name="Meet the solo builder" durationInFrames={140}>
      <OpeningScene />
    </Sequence>
    <Sequence name="Introduce the project" from={140} durationInFrames={200}>
      <ProjectScene />
    </Sequence>
    <Sequence name="Roles and focus" from={340} durationInFrames={260}>
      <FocusScene />
    </Sequence>
    <Audio
      name="ElevenLabs Roger narration"
      from={18}
      src={staticFile("narration.mp3")}
    />
    <BasicCaptions
      width={1600}
      style={{ position: "absolute", bottom: 105, translate: "160px 0px" }}
      captions={[
        {
          text: "Hi, I’m Ruihua,",
          startMs: 880,
          endMs: 2280,
          timestampMs: null,
          confidence: null,
          pageBreakAfter: true,
        },
        {
          text: "the solo builder behind team whardite.",
          startMs: 2280,
          endMs: 4860,
          timestampMs: null,
          confidence: null,
          pageBreakAfter: true,
        },
        {
          text: "I’m building a Rental Housing Law Navigator",
          startMs: 4860,
          endMs: 7180,
          timestampMs: null,
          confidence: null,
          pageBreakAfter: true,
        },
        {
          text: "to help people understand rental rules",
          startMs: 7180,
          endMs: 9520,
          timestampMs: null,
          confidence: null,
          pageBreakAfter: true,
        },
        {
          text: "and check the original sources.",
          startMs: 9520,
          endMs: 11620,
          timestampMs: null,
          confidence: null,
          pageBreakAfter: true,
        },
        {
          text: "I handle the design, development, and testing,",
          startMs: 11620,
          endMs: 14700,
          timestampMs: null,
          confidence: null,
          pageBreakAfter: true,
        },
        {
          text: "with a focus on clear answers backed by evidence.",
          startMs: 14700,
          endMs: 17840,
          timestampMs: null,
          confidence: null,
          pageBreakAfter: true,
        },
      ]}
    />
    <Interactive.Div
      name="Voice credit"
      style={{
        position: "absolute",
        bottom: 38,
        right: 144,
        color: "#A3B4A9",
        fontSize: 25,
      }}
    >
      AI narration · ElevenLabs
    </Interactive.Div>
  </AbsoluteFill>
);

export const MyComposition = () => (
  <Composition
    id="TeamIntro"
    component={TeamIntro}
    durationInFrames={600}
    fps={30}
    width={1920}
    height={1080}
  />
);
