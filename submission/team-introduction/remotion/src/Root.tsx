import { MyComposition } from "./Composition";
import { Folder } from "remotion";
import { OpeningComposition } from "./OpeningScene";
import { ProjectComposition } from "./ProjectScene";
import { FocusComposition } from "./FocusScene";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <MyComposition />
      <Folder name="Scenes">
        <OpeningComposition />
        <ProjectComposition />
        <FocusComposition />
      </Folder>
    </>
  );
};
