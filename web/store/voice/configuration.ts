import { API_ENDPOINT } from "store/endpoint";

export const defaultVoiceDocument = `---
id: your-unique-id
name: Your Display Name

model:
  api: realtime

inputs:
  name: Seth Juarez

tools:
  your_tool_name:
    type: function
    description: Your tool description
    parameters:
      - name: name_of_parameter
        type: string
        description: Your parameter description
        required: true
---
Your Markdown content goes here (using {{name}} for customer name).
`

export interface Configuration {
  id: string;
  name: string;
  default: boolean;
  content: string;
}

export class VoiceConfiguration {
  endpoint: string;
  configurations: Configuration[] = [];

  constructor() {
    this.endpoint = API_ENDPOINT;
  }

  async fetchConfigurations(): Promise<Configuration[]> {
    const response = await fetch(`${this.endpoint}/api/configurations`);
    if (!response.ok) {
      throw new Error("Failed to fetch configurations");
    }
    this.configurations = await response.json();
    return this.configurations;
  }
}