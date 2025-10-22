# Claude Code + Azure Deployment Setup Guide

## Prerequisites

- Python 3.8+
- VS Code with Claude Code extension
- Azure OpenAI Service access
- Azure Application Insights (optional for telemetry)

## 1. Install Claude Code Extension for VS Code

1. Open VS Code
2. Go to the Extensions tab (or press `Ctrl+Shift+X` / `Cmd+Shift+X`)
3. Search for "Claude Code"
4. Click Install
5. Reload VS Code if prompted

## 2. Install Dependencies

```bash
pip install -r requirements.txt
```


## 3. Environment Variables Setup

Create a `.env` file in the project root:

```bash
# Azure Application Insights (Mendatory)
azure_app_insights_connection_string=your-instrumentation-key-here

```

## 4. Configuration Files

### config.yaml`

In yaml that already exists in the repositor set the actual azure credentials

```yaml
# Model configuration
model_list:
    - model_name: deepseek
      litellm_params:
        model: azure/DeepSeek-V3.1
        api_base: <AZURE_OPENAI_ENDPOINT}>
        api_version: 2024-05-01-preview
        api_key: <AZURE_OPENAI_API_KEY>
# LiteLLM settings with custom logger
litellm_settings:
  callbacks: custom_logger.TokenLogger
```

### VS Code Settings (settings.json)

To configure VS Code settings:

1. Open VS Code
2. Go to **File → Preferences → Settings** (or press `Ctrl+,` / `Cmd+,`)
3. In the search bar, type "claude"
4. Click the **Open Settings (JSON)** button in the top right corner
5. Add the following configuration to your `settings.json` file:

```json
{
  "claude-code.environmentVariables": [
    {
      "name": "ANTHROPIC_API_KEY",
      "value": "sk-"
    },
    {
      "name": "ANTHROPIC_AUTH_TOKEN",
      "value": "sk-actual-token"
    },
    {
      "name": "ANTHROPIC_BASE_URL",
      "value": "http://localhost:4000"
    },
    {
      "name": "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC",
      "value": "1"
    }
  ],
  "claude-code.selectedModel": "deepseek"
}
```

## 5. Running the Setup

### Start LiteLLM Proxy Server

```bash
# Load environment variables and start server
litellm --config config.yaml --host 127.0.0.1 --port 4000
```

### Expected Output on Success

```
✅ SUCCESS: Azure Monitor configured successfully
📊 Application Insights telemetry is now active
INFO: Started server process [12345]
INFO: Waiting for application startup.
INFO: Application startup complete.
INFO: Uvicorn running on http://127.0.0.1:4000 (Press CTRL+C to quit)
```

## 6. Testing the Setup

1. **Verify LiteLLM Server**: Check that the server is running on port 4000
2. **Test Claude Code**: Open VS Code and use any Claude Code feature
3. **Check Logs**: Verify requests are being processed in the LiteLLM terminal
4. **Azure Telemetry**: If configured, check Azure Application Insights for logs

## 7. Security Best Practices

### Secure Configuration Practices

1. **Never commit API keys** to version control
2. **Use environment variables** for all sensitive data
3. **Rotate keys regularly** following your organization's security policy
4. **Monitor usage** through Azure Application Insights

## 8. Troubleshooting

### Common Issues

- **Port 4000 in use**: Change port in both config and VS Code settings
- **Authentication errors**: Verify Azure OpenAI credentials in `.env`
- **Connection refused**: Ensure LiteLLM server is running before using Claude Code

### Error Messages and Solutions

```
❌ ERROR: Azure Application Insights connection string not found
→ Set azure_app_insights_connection_string in .env file

❌ ERROR: Failed to configure Azure Monitor
→ Check Azure credentials and network connectivity

400 Invalid model name
→ Verify model configuration in config.yaml matches Azure deployment
```

## 9. Advanced Configuration

### Customizing the Logger

The `custom_logger.py` file provides:
- Pre-call logging for model requests
- Token usage tracking
- Azure Application Insights integration
- Structured logging format


## Support

For issues with:
- Azure OpenAI: Contact the team
- LiteLLM: Check [LiteLLM documentation](https://docs.litellm.ai/)
- Claude Code: VS Code extension support
- This setup: Review this guide and check error messages
