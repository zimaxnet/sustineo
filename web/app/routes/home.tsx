import type { Route } from "./+types/home";
import Settings from "components/settings";
import Setting from "components/setting";
import { TbArticle, TbSettingsCog } from "react-icons/tb";
import VoiceSettings from "components/voice/voicesettings";
import Actions from "components/actions";
import { version } from "store/version";
import Title from "components/title";
import { useEffect, useState } from "react";
import type { Message } from "store/voice/voice-client";
import { useUser } from "store/useuser";
import { useRealtime } from "components/voice/userealtime";
import { useEffortStore } from "store/effort";
import usePersistStore from "store/usepersiststore";
import styles from "./home.module.scss";
import AgentEditor from "components/voice/agenteditor";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { API_ENDPOINT } from "store/endpoint";
import Output from "components/output";

import VoiceTool from "components/voicetool";
import Effort from "components/effortlist";
import { data } from "store/work";

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

  const effort = usePersistStore(useEffortStore, (state) => state);

  const [lasFunctionCall, setLastFunctionCall] = useState<string | null>(null);

  const handleServerMessage = async (serverEvent: Message) => {
    if (serverEvent.type === "function") {
      console.log(JSON.parse(serverEvent.payload));
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
      //setLastFunctionCall(func.call_id);
      effort?.addEffort({
        id: func.call_id,
        type: "function",
        name: func.name,
        arguments: func.arguments,
      });

      const api = `${API_ENDPOINT}/api/agent/${user.key}/`;
      await fetch(api, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          call_id: func.call_id,
          id: func.id,
          name: func.name,
          arguments: func.arguments,
        }),
      });

    } else if (serverEvent.type === "user" || serverEvent.type === "assistant") {
        //console.log("serverEvent", serverEvent.type, serverEvent.payload);
        const msg = JSON.parse(serverEvent.payload);
        if (msg.content && msg.content.trim() !== "") {
          effort?.addEffort({
            id: msg.id,
            type: "message",
            role: msg.role,
            content: msg.content,
          });
        }
      } else if (serverEvent.type === "agent") {
        const payload = JSON.parse(serverEvent.payload);
        // everything except call_id and name
        effort?.addEffort({
            id: payload.id,
            type: "agent",
            agentName: payload.agentName,
            callId: payload.callId,
            name: payload.name,
            status: payload.status,
            statusType: payload.type,
            content: payload.content,
          });

        // check for message completion to add to output
      }
  };

  const { toggleRealtime, talking, sendRealtime, callState } = useRealtime(
    user,
    handleServerMessage
  );

  const handleVoice = async () => {
    if (callState === "idle") {
      effort?.clearEfforts();
    }
    toggleRealtime();
  };

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
    <main className={styles.home}>
      <Title text="sustineō" version={version} user={user} />
      <div className={styles.scratch}>
        <div className={styles.effort}>
          <Effort />
        </div>
        <div className={styles.output}>
          <Output data={data} />
        </div>
      </div>
      <Actions>
        <VoiceTool onClick={() => handleVoice()} />
      </Actions>
      <Settings>
        <Setting
          id={"voice-settings"}
          icon={<TbSettingsCog size={18} />}
          className={styles.voice}
        >
          <VoiceSettings />
        </Setting>
        <Setting
          id={"voice-agent-settings"}
          icon={<TbArticle size={18} />}
          className={styles.editor}
        >
          <QueryClientProvider client={queryClient}>
            <AgentEditor />
          </QueryClientProvider>
        </Setting>
      </Settings>
      {talking && <div>!!!!!!!!!!!!!!!</div>}
    </main>
  );
}
