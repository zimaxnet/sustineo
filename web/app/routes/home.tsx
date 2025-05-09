import type { Route } from "./+types/home";
import Settings from "components/settings";
import Setting from "components/setting";
import {
  TbArticle,
  TbSettingsCog,
  TbViewfinder,
  TbImageInPicture,
  TbAirBalloon,
} from "react-icons/tb";
import { VscClearAll } from "react-icons/vsc";
import VoiceSettings from "components/voice/voicesettings";
import Actions from "components/actions";
import { version } from "store/version";
import Title from "components/title";
import { useEffect, useRef, useState } from "react";
import type { Update } from "store/voice/voice-client";
import { useUser } from "store/useuser";
import { useRealtime } from "components/voice/userealtime";
import { useEffortStore } from "store/effort";
import usePersistStore from "store/usepersiststore";
import styles from "./home.module.scss";
import AgentEditor from "components/voice/agenteditor";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { API_ENDPOINT } from "store/endpoint";

import VoiceTool from "components/voicetool";
import Effort from "components/effortlist";
import Tool from "components/tool";
import { useOutputStore } from "store/output";
import { v4 as uuidv4 } from "uuid";
import Output from "components/output";
import {
  imageData,
  researchData,
  scenarioEffort,
  scenarioOutput,
  writerData,
} from "store/data";
import VideoImagePicker from "components/videoimagepicker";
import { HiOutlineVideoCamera } from "react-icons/hi2";
import { IoCameraOutline } from "react-icons/io5";
import FileImagePicker, {
  type FileInputHandle,
} from "components/fileimagepicker";
import { useLocation } from "react-router";

const queryClient = new QueryClient();

export function meta({}: Route.MetaArgs) {
  return [
    { title: "BuildEvents by Contoso" },
    { name: "description", content: "Making Things Happen since 1935" },
  ];
}

export default function Home() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const flags =
    queryParams
      .get("flags")
      ?.split(",")
      .map((i) => i.toLocaleLowerCase().trim()) || [];
  //console.log("Flags", flags);

  const { user, error } = useUser();
  const [showCapture, setShowCapture] = useState(false);
  const filePickerRef = useRef<FileInputHandle>(null);

  useEffect(() => {
    if (error) {
      console.error("Error fetching user data:", error);
    }
  }, [error]);

  const effort = usePersistStore(useEffortStore, (state) => state);
  const output = usePersistStore(useOutputStore, (state) => state);

  const addOutput = async (
    parent: string,
    agent: string,
    call_id: string,
    content: Array<Record<string, any>>
  ) => {
    console.log("Adding output", parent, agent, call_id, content);
    for (const item of content) {
      if (item.type === "text") {
        await sendRealtime({
          id: uuidv4(),
          type: "function_completion",
          call_id: call_id,
          output: item.value,
        });
        output?.addOutput(parent, agent, {
          id: uuidv4(),
          title: agent,
          value: 1,
          data: {
            id: uuidv4(),
            type: "text",
            value: item.value,
            annotations: item.annotations,
          },
          children: [],
        });
      } else if (item.type === "image") {
        await sendRealtime({
          id: uuidv4(),
          type: "function_completion",
          call_id: call_id,
          output: `Generated image as described by ${item.description}. It is ${item.size} and ${item.quality}. It has been saved and is currently being displayed to ${user.name}.`,
        });
        output?.addOutput(parent, agent, {
          id: uuidv4(),
          title: agent,
          value: 1,
          data: {
            id: uuidv4(),
            type: "image",
            description: item.description,
            image_url: item.image_url,
            size: item.size,
            quality: item.quality,
          },
          children: [],
        });
      }
    }
  };

  const handleServerMessage = async (serverEvent: Update): Promise<void> => {
    console.log(serverEvent);
    switch (serverEvent.type) {
      case "message":
        if (serverEvent.content) {
          effort?.addEffort(serverEvent);
        }
        break;
      case "function":
        // no need to await for this, just send it to the server
        sendRealtime({
          id: serverEvent.id,
          type: "function_completion",
          call_id: serverEvent.call_id,
          output:
            "This is a message from the function call that it is in progress. Acknowledge it internally but you don't have to say anything.",
        });

        effort?.addEffort(serverEvent);

        const api = `${API_ENDPOINT}/api/agent/${user.key}`;
        console.log("Sending function call to agent", api, serverEvent);
        await fetch(api, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            call_id: serverEvent.call_id,
            id: serverEvent.id,
            name: serverEvent.name,
            arguments: serverEvent.arguments,
          }),
        });
        break;
      case "agent":
        effort?.addEffort(serverEvent);
        if (serverEvent.content) {
          addOutput(
            serverEvent.name.toLowerCase().replaceAll(" ", "_"),
            serverEvent.name,
            serverEvent.call_id,
            serverEvent.content?.content
          );
        }
        break;
    }
  };

  const { toggleRealtime, analyzer, sendRealtime, callState } = useRealtime(
    user,
    handleServerMessage
  );

  const handleVoice = async () => {
    if (callState === "idle") {
      effort?.clearEfforts();
      output?.reset();
    }
    toggleRealtime();
  };

  useEffect(() => {
    if (callState === "call" && analyzer && canvasRef.current) {
      console.log("Starting audio visualization");
      const canvas = canvasRef.current;
      const context = canvas.getContext("2d");
      const bufferLength = analyzer.frequencyBinCount;
      const dataArray = new Uint8Array(bufferLength);
      const width = canvas.width;
      const height = canvas.height;
      console.log("canvas", width, height);
      if (context) {
        const draw = () => {
          if (callState === "call" && analyzer) {
            requestAnimationFrame(draw);
          }
          if (!analyzer) return;

          context.clearRect(0, 0, width, height);
          context.fillStyle = "rgb(255, 255, 255, 0)";
          context.fillRect(0, 0, width, height);

          analyzer.getByteFrequencyData(dataArray);
          //console.log("Data Array", dataArray);
          context.strokeStyle = "rgb(255, 255, 255, 0.1)";
          for (let i = 0; i < bufferLength; i++) {
            const barHeight = dataArray[i];
            context.beginPath();

            context.arc(width / 2, height / 2, barHeight, 0, Math.PI * 2);
            context.stroke();

            //context.fillRect(i * 2, height - barHeight, 1, barHeight);
          }
        };
        draw();
      }
    }
  }, [analyzer, callState]);

  return (
    <QueryClientProvider client={queryClient}>
      <canvas
        ref={canvasRef}
        className={styles.canvas}
        width={300}
        height={300}
      />
      <main className={styles.home}>
        <Title
          text="BuildEvents"
          subtitle="by Contoso"
          version={version}
          user={user}
        />
        <div className={styles.scratch}>
          <div className={styles.effort}>
            <Effort />
          </div>
          <div className={styles.output}>
            {output && output.output && output.output.children.length > 0 && (
              <Output data={output.output} />
            )}
          </div>
        </div>
        <Actions>
          {flags.includes("debug") ? (
            <>
              <Tool
                icon={<IoCameraOutline size={18} title={"Capture Image"} />}
                onClick={() => {
                  filePickerRef.current?.activateFileInput();
                }}
                title={"Capture Image"}
              />
              <Tool
                icon={
                  <HiOutlineVideoCamera size={18} title={"Capture Image"} />
                }
                onClick={() => {
                  setShowCapture((prev) => !prev);
                }}
                title={"Capture Image"}
              />
              <Tool
                icon={<VscClearAll size={18} title={"Reset"} />}
                onClick={() => {
                  effort?.clearEfforts();
                  output?.reset();
                }}
                title={"Reset"}
              />
              <Tool
                icon={<TbImageInPicture size={18} title={"Add Image"} />}
                onClick={() => {
                  output?.addOutput("gpt-image-1_agent", "GPT Image Agent", {
                    id: uuidv4(),
                    title: "GPT Image Agent",
                    value: 1,
                    data: imageData,
                    children: [],
                  });
                }}
                title={"Add Image"}
              />
              <Tool
                icon={<TbArticle size={18} title={"Add Article"} />}
                onClick={() => {
                  output?.addOutput(
                    "content_writer_agent",
                    "Content Writer Agent",
                    {
                      id: uuidv4(),
                      title: "Content Writer Agent",
                      value: 1,
                      data: writerData,
                      children: [],
                    }
                  );
                }}
                title={"Add Article"}
              />
              <Tool
                icon={<TbViewfinder size={18} title={"Add Research"} />}
                onClick={() => {
                  output?.addOutput("research_agent", "Research Agent", {
                    id: uuidv4(),
                    title: "Research Agent",
                    value: 1,
                    data: researchData,
                    children: [],
                  });
                }}
                title={"Add Research"}
              />
              <Tool
                icon={<TbAirBalloon size={18} title={"Reset Event Scenario"} />}
                onClick={() => {
                  output?.reset();
                  output?.addRoot(scenarioOutput);
                  effort?.clearEfforts();
                  effort?.addEffortList(scenarioEffort);
                }}
                title={"Reset Event Scenario"}
              />
            </>
          ) : (
            <></>
          )}
          <VoiceTool
            onClick={() => handleVoice()}
            className={callState === "idle" ? styles.idle : styles.call}
          />
        </Actions>
        {flags.includes("tools") ? (
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
              <AgentEditor />
            </Setting>
          </Settings>
        ) : (
          <></>
        )}
      </main>
      <VideoImagePicker
        show={showCapture}
        setShow={setShowCapture}
        setCurrentImage={(image) => {
          console.log("Image selected", image);
        }}
      />
      <FileImagePicker
        ref={filePickerRef}
        setCurrentImage={(image) => {
          console.log("Image selected", image);
        }}
      />
    </QueryClientProvider>
  );
}
