def parse_agents(text):
    agents = []
    current = None

    for line in text.splitlines():
        line = line.strip()

        # When AGENT starts — begin a new dict
        if line == "AGENT":
            current = {}
            continue

        # When END comes — push dict to list
        if line == "END":
            if current:
                agents.append(current)
                current = None
            continue

        # Ignore empty lines
        if not line:
            continue

        # Parse key: value
        if ":" in line and current is not None:
            key, value = line.split(":", 1)
            current[key.replace(" ", "_").lower().strip()] = value.strip()

    return agents



class AgentResponseStreamingParser:
    def __init__(self):
        self.buffer = ""
        self.agent_name = None
        self.emotion = None
        self.in_response = False
        self.meta_sent = False

    def process_token(self, token: str):
        # IMPORTANT: preserve space
        self.buffer += token

        # Step 1: Extract AGENT and EMOTION (once)
        if not self.in_response:
            if self.agent_name is None:
                self.agent_name = self._extract_line("AGENT")

            if self.emotion is None:
                self.emotion = self._extract_line("EMOTION")

            if "RESPONSE:" in self.buffer:
                # Response starts here
                after = self.buffer.split("RESPONSE:", 1)[1]

                if not self.meta_sent:
                    print({
                        "event": "agent_start",
                        "agent": self.agent_name,
                        "emotion": self.emotion
                    })
                    self.meta_sent = True

                self.in_response = True
                self.buffer = ""

                if after.strip():
                    print({
                        "event": "token",
                        "content": after
                    })
                return

        # Step 2: Stream response tokens
        if self.in_response:
            if "END" in self.buffer:
                print({"event": "agent_end"})
                return

            print({
                "event": "token",
                "content": token
            })

    def _extract_line(self, key: str):
        marker = f"{key}:"
        if marker not in self.buffer:
            return None

        after = self.buffer.split(marker, 1)[1]
        if "\n" not in after:
            return None

        return after.split("\n", 1)[0].strip()

