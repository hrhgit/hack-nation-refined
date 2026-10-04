import {
  AbsoluteFill,
  Composition,
  Easing,
  Interactive,
  interpolate,
  useCurrentFrame,
} from "remotion";

export const ProjectScene: React.FC = () => {
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
        name="Project label"
        style={{
          color: "#A8CFB9",
          fontSize: 38,
          letterSpacing: 5,
          fontWeight: 600,
        }}
      >
        WHAT I’M BUILDING
      </Interactive.Div>
      <Interactive.Div
        name="Project title"
        style={{
          marginTop: 40,
          fontSize: 140,
          fontWeight: 700,
          lineHeight: 1.06,
          letterSpacing: -5,
          opacity: interpolate(frame, [0, 13], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
          translate: interpolate(frame, [0, 18], ["0px 24px", "0px 0px"], {
            easing: Easing.bezier(0.16, 1, 0.3, 1),
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      >
        Rental Housing
        <br />
        Law Navigator
      </Interactive.Div>
      <Interactive.Div
        name="Project purpose"
        style={{
          marginTop: 40,
          fontSize: 62,
          lineHeight: 1.28,
          color: "#D1D9D2",
          opacity: interpolate(frame, [16, 30], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      >
        Understand the rules. Check the sources.
      </Interactive.Div>
      <Interactive.Svg
        name="House illustration"
        width={330}
        height={330}
        viewBox="0 0 330 330"
        style={{
          position: "absolute",
          right: 160,
          top: 320,
          opacity: interpolate(frame, [8, 27], [0, 0.7], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      >
        <Interactive.Path
          name="House roof"
          d="M 40 150 L 165 42 L 290 150"
          fill="none"
          stroke="#A8CFB9"
          strokeWidth={9}
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        <Interactive.Path
          name="House walls"
          d="M 70 143 L 70 283 L 259 283 L 259 143 M 140 283 L 140 204 L 191 204 L 191 283"
          fill="none"
          stroke="#A8CFB9"
          strokeWidth={9}
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </Interactive.Svg>
    </AbsoluteFill>
  );
};

export const ProjectComposition = () => (
  <Composition
    id="02-Project"
    component={ProjectScene}
    durationInFrames={200}
    fps={30}
    width={1920}
    height={1080}
  />
);
