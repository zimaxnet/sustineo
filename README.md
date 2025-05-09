# sustineo
Ego sustineo, ego sum tuus personalis AI adiutor.
I support, I am your personal AI assistant.

## Feature Flags
The app has two feature flags when running the app in production mode:
- `?flags=debug` - enables debug mode - adds pre-population tools for resetting the app
- `?flags=tools` - enables prompt + agent selection tools for the voice agent
- `?flags=tools,debug` - enables both debug and tools mode

```curl
http://example.com/?flags=debug,tools
```

## Restarting the container

List revision:

```bash
az containerapp revision list --name sustineo-api --resource-group contoso-concierge --query [].name | tr -d '"'
```
Output example
```bash
[
  sustineo-api--0000008
]
```

This will give you the revision name you need to restart.

Restart Revision:
```bash
az containerapp revision restart --name sustineo-api --resource-group contoso-concierge --revision sustineo-api--0000008
```

Output example
```bash
"Restart succeeded"
```


## TODO List
- gpt-image-1 editor (S)
- sora integration (S)
- save output to file function (S)
- agent definitions (code + file) (A)
- scenario generation (A)