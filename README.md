# Rezultati Discord Bot

### Requirements:
* `docker`
* `docker-compose`
* Discord bot token

Create an `.env` file in the root with the following variables e.g:

```
DISCORD_TOKEN=XXXX     # obtained from discord developer portal
LOG_CHANNEL_ID=XXXX    # private channel for logs
SECRET_SERVER=XXXX     # special server with easter egg commands (shh don't worry about it)
```

### Run:
`docker-compose up -d`

### Usage:
```
prefiks : sudo
komande:
prati [url]
otprati [url]
otprati sve
strane -- sve strane koje pratis
sve -- sve strane u bazi
users -- svi korisnici u bazi
help -- ova poruka
aliases -- aliasi za komande
owner -- bot owner
primer : sudo prati http://www.matf.bg.ac.rs/p/maricm/pocetna/
```
