# Running the bot from a local Linux terminal (token kept in AWS)

## 1. Once: install
Debian/Ubuntu (other distros: the same packages under their names):
```bash
sudo apt-get install -y python3 python3-venv git redis-server awscli
sudo systemctl enable --now redis-server
git clone https://github.com/Itachi1998/KoganeCGbot.git && cd KoganeCGbot
git checkout claude/add-files-ai-folder-vrijsg        # or main, once merged
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
```
Python 3.10 or newer.

## 2. Once: put the token in AWS
Log the terminal in to AWS (`aws configure` with an IAM user's keys, or `aws sso login --profile you`).
Then store the token (SSM Parameter Store standard parameters are free; Secrets Manager is
$0.40 a secret a month):
```bash
aws ssm put-parameter --name /kogane/discord-token --type SecureString --value 'PASTE-TOKEN'
```
or `aws secretsmanager create-secret --name kogane/discord --secret-string 'PASTE-TOKEN'`.

The AWS identity the bot runs as only needs `ssm:GetParameter` on that parameter (and
`kms:Decrypt` if you used your own KMS key instead of the default `aws/ssm`), or
`secretsmanager:GetSecretValue` on the secret.

## 3. Once: settings
Create `deploy/.env` (git ignores it):
```bash
DISCORD_TOKEN_SSM=/kogane/discord-token        # or DISCORD_TOKEN_SECRET=kogane/discord
AWS_REGION=us-east-1                           # where you stored it
# AWS_PROFILE=you                              # if you use a named profile / SSO
CULLING_DB=sqlite                              # the game is saved in ~/kogane-data/culling.db
```

## 4. Run
```bash
deploy/run_local.sh
```
You should see `Token: from SSM parameter ...`, the cogs loading,
`Storage: sqlite (...), battle cache: redis` and `Bot is ready as ...`. Stop with Ctrl+C.
Keep it running after you log out: `tmux new -s kogane` then `deploy/run_local.sh`
(detach with Ctrl+B D), or install `deploy/kogane-ai.service` as a systemd service.

In Discord: the Developer Portal needs **Message Content** and **Server Members** intents on, and
the bot needs **Create Public Threads** and **Create Private Threads** (lobbies) besides sending
messages. Then type `,sync` in your server as the bot's owner. Run only one copy of the bot per token.
