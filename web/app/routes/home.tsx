import type { Route } from "./+types/home";
import Settings from "components/settings";
import Setting from "components/setting";
import {
  TbArticle,
  TbUserHexagon,
  TbArrowBigRight,
  TbSettingsCog,
} from "react-icons/tb";
import VoiceSettings from "components/voice/voicesettings";
import Actions from "components/actions";
import Tool from "components/tool";
import Canvas from "components/canvas";
import { version } from "store/version";
import Title from "components/title";
import { useEffect, useState } from "react";
import type { Message } from "store/voice/voice-client";
import { useUser } from "store/useuser";
import { useRealtime } from "components/voice/userealtime";
import styles from "./home.module.scss";
import AgentEditor from "components/voice/agenteditor";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

const queryClient = new QueryClient();

export function meta({}: Route.MetaArgs) {
  return [
    { title: "sustineō" },
    { name: "description", content: "Your Digital Support Agent" },
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
          output:
            "Working on it - will continue to update as I go. Feel free to work on other tasks in the meantime. Make sure to let the user know you are working on it and can do other tasks.",
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

  const sendCall = async (output: string) => {
    if (lasFunctionCall) {
      sendRealtime({
        type: "function",
        payload: JSON.stringify({
          call_id: lasFunctionCall,
          output: output,
        }),
      });
    } else {
      console.log("No function call to send.");
    }
  };

  return (
    <QueryClientProvider client={queryClient}>
      <main>
        <Title text="sustineō" version={version} user={user} />

        <Actions>
          <Tool
            icon={<TbUserHexagon size={24} />}
            onClick={() => toggleRealtime()}
          />
          <Tool
            icon={<TbArrowBigRight size={24} />}
            onClick={() =>
              sendCall(
                "I need more information to continue. Please ask the user to provide details about the product pricing."
              )
            }
          />
          <Tool
            icon={<TbArrowBigRight size={24} />}
            onClick={() =>
              sendCall(
                "All done - let the user know that the task is complete and they can ask for more help if needed. They can click on the icon on the top right to see the result."
              )
            }
          />
        </Actions>
        <Settings>
          <Setting
            id={"voice-settings"}
            icon={<TbSettingsCog size={24} />}
            className={styles.voice}
          >
            <VoiceSettings />
          </Setting>
          <Setting
            id={"voice-agent-settings"}
            icon={<TbArticle size={24} />}
            className={styles.editor}
          >
            <AgentEditor />
          </Setting>
        </Settings>
        {talking && <div>!!!!!!!!!!!!!!!</div>}
      </main>
    </QueryClientProvider>
  );
}
