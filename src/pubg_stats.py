import pickle
import os
import warnings
import datetime
import discord

from pubg_python import PUBG, Shard, exceptions as PUBG_Exceptions

class PUBG_Stats:
    season_file = 'seasons.dat'
    season_data_expire = 15
    api = None
    seasons = None
    current_season = None
    game_modes = ['solo', 'solo_fpp', 'duo', 'duo_fpp', 'squad', 'squad_fpp']

    def __init__(self, token, season_file=None, season_data_expire=None):
        self.api = PUBG(token, Shard.STEAM)
        if season_file is not None:
            self.season_file = season_file

        if season_data_expire is not None:
            self.season_data_expire = int(season_data_expire)

        self._check_seasons()



    def _update_seasons_file(self):
        print(f"Updating seasons file")
        self.seasons = self.api.seasons()
        with open(self.season_file, 'wb') as file:
            pickle.dump(self.seasons, file)

        self._set_current_season()

    def _load_seasons_file(self):
        print(f"Loading seasons file")
        with open(self.season_file, 'rb') as file:
            self.seasons = pickle.load(file)

        self._set_current_season()

    def _set_current_season(self):
        if self.seasons is None:
            warnings.warn("Attempted to set current season with no season data")
            return

        for season in self.seasons:
            if season.attributes['isCurrentSeason']:
                self.current_season = season
                print(f"Found current season: {season.id}")
                break


    def _check_seasons(self):
        if not os.path.isfile(self.season_file):
            self._update_seasons_file()

        if datetime.datetime.fromtimestamp(os.path.getmtime(self.season_file)) < datetime.datetime.now() - datetime.timedelta(days = self.season_data_expire):
            self._update_seasons_file()
            return

        if self.seasons is None:
            self._load_seasons_file()
            return

    def get_current_season(self):
        self._check_seasons()
        return self.current_season

    def _format_kd(self, kills, deaths):
        if kills == 0 and deaths == 0:
            return None

        if deaths == 0:
            return kills

        return round(kills/deaths,2)

    def get_player(self, player_name=None, player_id=None):
        if player_id is not None:
            warnings.warn(f"Unimplented feature get_player by id")
            return None

        if player_name is not None:
            try:
                players = self.api.players().filter(player_names=[player_name])
                if players[0] is not None:
                    return players[0]
            except PUBG_Exceptions.NotFoundError:
                return None

        return None

    def get_stats(self, player, member=None):
        if player is None:
            return None

        data = self.api.seasons(self.get_current_season().id, player_id=player.id).get()

        stats_dict = {
            'title': f"{player.name}'s Stats",
            'fields': []
        }

        if member is not None:
            stats_dict['thumbnail'] = {
                'url': str(member.avatar_url)
            }

        weekly_wins = 0
        season_wins = 0
        season_kills = 0
        season_matches = 0
        season_losses = 0

        mode_data = []

        for mode in self.game_modes:
            losses = getattr(data, mode).losses
            wins = getattr(data, mode).wins
            matches = losses + wins
            kills = getattr(data, mode).kills
            kd = self._format_kd(kills, losses)

            season_kills += kills
            season_matches += matches
            season_losses += losses
            season_wins += wins
            weekly_wins += getattr(data,mode).weekly_wins
            if matches != 0:
                mode_data.append({
                    'kills': kills,
                    'matches': matches,
                    'losses': losses,
                    'wins': wins,
                    'kd': kd,
                    'mode': mode
                })

        mode_data = sorted(mode_data, key=lambda item: item['matches'],reverse=True)

        for info in mode_data:
            stats_dict['fields'].append({
                'name': f"{info['mode'].title()}:",
                'value': f"`Matches:` {info['matches']}  `Wins:` {info['wins']}  `K/D:` {info['kd']}"
            })

        season_kd = self._format_kd(season_kills, season_losses)

        if season_kd <= 0.4:
            stats_dict['color'] = discord.Color.red().value
        elif season_kd <= 0.5:
            stats_dict['color'] = discord.Color.gold().value
        else:
            stats_dict['color'] = discord.Color.green().value

        stats_dict['fields'].insert(0,{
            'name': f"Season Wins:",
            'value': f"`Weekly:` **{weekly_wins}**  `Total:` **{season_wins}**  `K/D:` **{season_kd}**",
            'inline': True
        })

        return stats_dict