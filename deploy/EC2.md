# Running the new bot on an EC2 instance

The bot only makes outbound connections (to Discord), so the instance's security group needs no
inbound rules except SSH for you. A `t3.small` (2 GB) is plenty for testing; `t3.micro` works but
is tight once Docker builds numpy.

## 1. Discord settings (once)
1. <https://discord.com/developers/applications> → your application → **Bot**:
   - Turn on **Message Content Intent** and **Server Members Intent**. The bot asks for both; without
     them it fails to log in with `PrivilegedIntentsRequired`.
   - **Reset Token** and copy it (it goes in `deploy/.env`).
2. **OAuth2 → URL Generator**: scopes `bot` and `applications.commands`; bot permissions **Send
   Messages**, **Send Messages in Threads**, **Create Public Threads**, **Embed Links**, **Read Message
   History**, **Use Application Commands**. Open the URL and add the bot to your test server.

## 2. Option A: Docker (recommended)
Amazon Linux 2023:
```bash
sudo dnf install -y docker git
sudo systemctl enable --now docker
sudo usermod -aG docker ec2-user && newgrp docker
sudo mkdir -p /usr/local/lib/docker/cli-plugins
sudo curl -SL https://github.com/docker/compose/releases/download/v2.29.7/docker-compose-linux-x86_64 \
     -o /usr/local/lib/docker/cli-plugins/docker-compose
sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
```
(Ubuntu: `sudo apt-get install -y docker.io docker-compose-v2 git`.)

Then:
```bash
git clone https://github.com/Itachi1998/KoganeCGbot.git && cd KoganeCGbot
git checkout claude/add-files-ai-folder-vrijsg        # or main, once it is merged
cp deploy/.env.example deploy/.env && nano deploy/.env   # paste DISCORD_TOKEN
docker compose -f deploy/docker-compose.yml up -d --build
docker compose -f deploy/docker-compose.yml logs -f bot
```
You should see `Cog loaded: ...`, `Storage: sqlite (/data/culling.db), battle cache: redis` and
`Bot is ready as ...`.

Update to new code: `git pull && docker compose -f deploy/docker-compose.yml up -d --build`.
Back up the game: `docker compose -f deploy/docker-compose.yml cp bot:/data/culling.db ./culling-backup.db`.

## 2. Option B: no Docker (systemd)
```bash
sudo dnf install -y python3.12 python3.12-pip git redis6
sudo systemctl enable --now redis6
git clone https://github.com/Itachi1998/KoganeCGbot.git && cd KoganeCGbot
git checkout claude/add-files-ai-folder-vrijsg
python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt
mkdir -p ~/kogane-data
cp deploy/.env.example deploy/.env && nano deploy/.env
sudo cp deploy/kogane-ai.service /etc/systemd/system/ && sudo systemctl daemon-reload
sudo systemctl enable --now kogane-ai && journalctl -u kogane-ai -f
```

## 3. In Discord
1. As the bot's owner, type `,sync` in your test server. Slash commands appear in that server at
   once (globally within about an hour).
2. Try: `/create` → Spin, `/profile`, `/skills`, `/learn colony`, `/look`, `/go`,
   `/lobby create` → join a team → Ready Up → **Hunt** (move toward a curse first; `/look` shows
   where they are) or **Spar**.
3. Run only ONE copy of the bot per token: two processes would both answer every command.

## 4. Switching to DynamoDB later
1. Give the instance an IAM role allowing `dynamodb:*Item`, `dynamodb:Query`, `dynamodb:Scan`,
   `dynamodb:BatchWriteItem`, `dynamodb:DescribeTable` and `dynamodb:CreateTable` on
   `arn:aws:dynamodb:<region>:<account>:table/CullingGame*`.
2. Stop the bot, then copy everything across (creates the table):
   `docker compose -f deploy/docker-compose.yml run --rm bot python -m ai.migrate --from sqlite:/data/culling.db --to dynamodb:CullingGame --create-table`
3. Set `CULLING_DB=dynamodb` and `AWS_REGION` in `deploy/.env`, start the bot again.
See `ai/STORAGE.md` for the table design and what it costs.
