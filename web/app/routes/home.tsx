import { API_ENDPOINT, WS_ENDPOINT } from "store/endpoint";

import type { Route } from "./+types/home";
import Settings from "components/settings";
import Setting from "components/setting";
import {
  TbSettingsPause,
  TbSettingsBolt,
  TbUserHexagon,
  TbEngine,
} from "react-icons/tb";
import VoiceSettings from "components/voice/voicesettings";
import Actions from "components/actions";
import Tool from "components/tool";
import Canvas from "components/canvas";
import { version } from "store/version";
import Title from "components/title";
import { useEffect, useRef, useState } from "react";
import type { Message } from "store/voice/voice-client";
import VoiceClient from "store/voice/voice-client";
import { useLocalStorage } from "store/uselocalstorage";
import { defaultConfiguration, type VoiceConfiguration } from "store/voice";
import useUser from "store/useuser";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "Contoso Social" },
    { name: "description", content: "Contoso Intelligent Social Application" },
  ];
}

export default function Home() {
  const [user, isLoading, error] = useUser();
  useEffect(() => {
    if (error) {
      console.error("Error fetching user data:", error);
    }
  }, [error]);

  const [settings, setSettings, resetSettings] =
    useLocalStorage<VoiceConfiguration>("voice-settings", defaultConfiguration);

  const [callState, setCallState] = useState<"idle" | "call">("idle");
  const voiceRef = useRef<VoiceClient | null>(null);

  const handleServerMessage = async (serverEvent: Message) => {
    console.log("serverEvent", serverEvent);
  };

  const startRealtime = async () => {
    if (voiceRef.current) {
      await voiceRef.current.stop();
      voiceRef.current = null;
    }

    if (!voiceRef.current) {
      const endpoint = WS_ENDPOINT.endsWith("/")
        ? WS_ENDPOINT.slice(0, -1)
        : WS_ENDPOINT;

      voiceRef.current = new VoiceClient(
        `${endpoint}/api/voice`,
        handleServerMessage
      );

      await voiceRef.current.start(settings.inputDeviceId);
      const message = {
        user: user!.name,
        threshold: settings.threshold,
        silence: settings.silence,
        prefix: settings.prefix,
      };

      await voiceRef.current.sendUserMessage(JSON.stringify(message));
      await voiceRef.current.sendCreateResponse();
      setCallState("call");
    }
  };

  const stopRealtime = async () => {
    if (voiceRef.current) {
      await voiceRef.current.stop();
      voiceRef.current = null;
      setCallState("idle");
    }
  };

  const toggleRealtime = async () => {
    if (callState === "idle") {
      await startRealtime();
    }
    if (callState === "call") {
      await stopRealtime();
    }
  };

  return (
    <main>
      <Title text="Contoso Social" version={version} user={user} />
      <Canvas />
      <Actions>
        <Tool
          icon={<TbUserHexagon size={24} />}
          onClick={() => toggleRealtime()}
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
    </main>
  );
}
