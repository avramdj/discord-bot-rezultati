import config

invalid_url = "Nije validan url 😔"
need_url = "Treba mi url 💅"
already_following = "Vec pratis tu stranu 😵"
success_unfollow = "Otpraceno 👏"
success_follow = "Pratim 👀"
following_zero = "Ne pratis ni jednu stranu 😢"
not_static = "ne mogu da pratim dinamicki html, teraj avrama da predje na selenium"
page_changed = "Strana se promenila 😍😍😍 "
no_pages = "Nema strana"
no_users = "Nema korisnika"
db_error = "Greska u bazi 😰"
page_too_big = "Fajl je prevelik 💧💧💧"
request_error = "Greska prilikom dohvatanj strane 🔎 :/"
bot_owner = "Created by https://github.com/avramdj"
rebooting = (
    "Watch nije pokrenut vise of "
    + str(config.watch_check_timer / 60)
    + " minuta, restartujem..."
)
deleted_account = "Ne postoji u bazi, brisem sve strane tog korisnika..."

aliases = """
aliases:
`prati` = `zaprati`, ` + `
`otprati` = ` - `
`strane` = `list`
`sve` = `links`
`users` = `korisnici`
`help` = ` ? `
"""

command_list = """
prefiks : `sudo`
komande:
`prati [url]`
`otprati [url]`
`otprati sve`
`strane` -- sve strane koje pratis
`sve` -- sve strane u bazi
`users` -- svi korisnici u bazi
`help` -- ova poruka
`aliases` -- aliasi za komande
`owner` -- bot owner
primer : `sudo prati http://www.matf.bg.ac.rs/p/maricm/pocetna/`
"""
