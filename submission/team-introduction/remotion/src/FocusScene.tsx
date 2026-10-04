import {
  AbsoluteFill,
  Composition,
  Easing,
  Interactive,
  interpolate,
  useCurrentFrame,
} from "remotion";

export const FocusScene: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill
      style={{
        padding: "234px 144px 190px",
        color: "#F5F2EA",
        fontFamily: "Arial, Helvetica, sans-serif",
      }}
    >
      <Interactive.Div
        name="Responsibilities"
        style={{
          color: "#A8CFB9",
          fontSize: 68,
          fontWeight: 500,
          opacity: interpolate(frame, [0, 12], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      >
        Design. Develop. Test.
      </Interactive.Div>
      <Interactive.Div
        name="Evidence first focus"
        style={{
          marginTop: 64,
          fontSize: 140,
          fontWeight: 700,
          lineHeight: 1.06,
          letterSpacing: -5,
          opacity: interpolate(frame, [8, 23], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
          translate: interpolate(frame, [8, 29], ["0px 26px", "0px 0px"], {
            easing: Easing.bezier(0.16, 1, 0.3, 1),
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      >
        Clear answers.
        <br />
        Backed by evidence.
      </Interactive.Div>
      <Interactive.Div
        name="Closing identity"
        style={{
          marginTop: 38,
          fontSize: 48,
          color: "#D1D9D2",
          opacity: interpolate(frame, [60, 78], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      >
        Ruihua He · Team whardite
      </Interactive.Div>
    </AbsoluteFill>
  );
};

export const FocusComposition = () => (
  <Composition
    id="03-Focus"
    component={FocusScene}
    durationInFrames={260}
    fps={30}
    width={1920}
    height={1080}
  />
);
