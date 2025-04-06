import styles from "./monaco.module.scss";
import { Editor } from "@monaco-editor/react";
import { VscNewFile, VscSave, VscStarEmpty } from "react-icons/vsc";

const Monaco = () => {

  return (
    <div className={styles.container}>
      <div className={styles.toolbar}>
        <div>
          <select
            id="device"
            name="device"
            className={styles.promptyselect}
            title="Select a device"
          >
            <option value="markdown">Markdown</option>
            <option value="json">JSON</option>
            <option value="javascript">JavaScript</option>
            <option value="typescript">TypeScript</option>
            <option value="python">Python</option>
            <option value="html">HTML</option>
            <option value="css">CSS</option>
          </select>
        </div>
        <button className={styles.icon} title="New">
          <VscNewFile size={22} />
        </button>
        <button className={styles.icon} title="Save">
          <VscSave size={22} />
        </button>
        <button className={styles.icon} title="Set As Default">
          <VscStarEmpty size={22} />
        </button>
      </div>
      <Editor height="70vh" defaultLanguage="markdown" />
    </div>
  );
};

export default Monaco;
