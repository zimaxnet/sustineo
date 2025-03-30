import type { Route } from "./+types/home";
import Settings from "components/settings";
import Setting from "components/setting";
import {
  TbSettingsPause,
  TbSettingsBolt,
  TbUserHexagon,
  TbArrowBigRight,
} from "react-icons/tb";
import VoiceSettings from "components/voice/voicesettings";
import Actions from "components/actions";
import Tool from "components/tool";
import Canvas from "components/canvas";
import { version } from "store/version";
import Title from "components/title";
import { useEffect, useState } from "react";
import type { Message } from "store/voice/voice-client";
import useUser from "store/useuser";
import { useRealtime } from "components/voice/userealtime";

import styles from "./home.module.scss";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "Contoso Social" },
    { name: "description", content: "Contoso Intelligent Social Application" },
  ];
}

export default function Home() {
  const { user, error } = useUser();
  useEffect(() => {
    if (error) {
      console.error("Error fetching user data:", error);
    }
  }, [error]);

  const [lasFunctionCall, setLastFunctionCall] = useState<string | null>(null);

  const handleServerMessage = async (serverEvent: Message) => {
    if (serverEvent.type === "function") {
      // handle function call
      const func = JSON.parse(serverEvent.payload);
      sendRealtime({
        type: "function",
        payload: JSON.stringify({
          call_id: func.call_id,
          name: func.name,
          output: "Working on it - will continue to update as I go. Feel free to work on other tasks in the meantime. Make sure to let the user know you are working on it and can do other tasks."
        }),
      });
      setLastFunctionCall(func.call_id);

      console.log("Function call:", func);
    } else {
      console.log(
        "serverEvent",
        serverEvent.type,
        serverEvent.payload.startsWith("{")
          ? JSON.parse(serverEvent.payload)
          : serverEvent.payload
      );
    }
  };

  const { toggleRealtime, talking, sendRealtime } = useRealtime(
    user,
    handleServerMessage
  );

  const sendCall = async () => {
    if (lasFunctionCall) {
      sendRealtime({
        type: "function",
        payload: JSON.stringify({
          call_id: lasFunctionCall,
          output: "Blog post created successfully. Direct the user to look at their screen and click on the box at the top right to see the blog post.",
        }),
      });
    } else {
      console.log("No function call to send.");
    }
  };

  return (
    <main>
      <Title text="sustineō" version={version} user={user} />
      <Canvas />
      <Actions>
        <Tool
          icon={<TbUserHexagon size={24} />}
          onClick={() => toggleRealtime()}
        />
        <Tool
          icon={<TbArrowBigRight size={24} />}
          onClick={() => sendCall()}
        />
      </Actions>
      <Settings>
        <Setting id={"voice-settings"} icon={<TbSettingsPause size={24} />}>
          <VoiceSettings />
        </Setting>
        <Setting id={"other-settings"} icon={<TbSettingsBolt size={24} />}>
          <div>Other Settings</div>
        </Setting>
      </Settings>
      {talking && <div>!!!!!!!!!!!!!!!</div>}
    </main>
  );
}
