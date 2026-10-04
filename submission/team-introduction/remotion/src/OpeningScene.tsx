import {
  AbsoluteFill,
  Composition,
  Easing,
  Interactive,
  interpolate,
  useCurrentFrame,
} from "remotion";

export const OpeningScene: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill
      style={{
        padding: "245px 144px 190px",
        color: "#F5F2EA",
        fontFamily: "Arial, Helvetica, sans-serif",
      }}
    >
      <Interactive.Div
        name="Introduction label"
        style={{
          color: "#A8CFB9",
          fontSize: 38,
          letterSpacing: 5,
          fontWeight: 600,
        }}
      >
        MEET THE BUILDER
      </Interactive.Div>
      <Interactive.Div
        name="Ruihua He"
        style={{
          marginTop: 50,
          fontSize: 180,
          lineHeight: 1.06,
          fontWeight: 700,
          letterSpacing: -8,
          opacity: interpolate(frame, [0, 16], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
          translate: interpolate(frame, [0, 22], ["0px 28px", "0px 0px"], {
            easing: Easing.bezier(0.16, 1, 0.3, 1),
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      >
        Ruihua He
      </Interactive.Div>
      <Interactive.Div
        name="Solo participant"
        style={{
          marginTop: 46,
          fontSize: 72,
          lineHeight: 1.2,
          color: "#D1D9D2",
          opacity: interpolate(frame, [8, 22], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      >
        Solo builder · Team whardite
      </Interactive.Div>
      <Interactive.Div
        name="Opening accent"
        style={{
          marginTop: 56,
          width: interpolate(frame, [10, 35], [0, 220], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
          height: 8,
          backgroundColor: "#A8CFB9",
          borderRadius: 4,
        }}
      />
    </AbsoluteFill>
  );
};

export const OpeningComposition = () => (
  <Composition
    id="01-Builder"
    component={OpeningScene}
    durationInFrames={140}
    fps={30}
    width={1920}
    height={1080}
  />
);
