class PhaseDescription:
    def __init__(self, rounds=None, immunity_types=None, config_mutations=None, should_summarise_phase=True, discussion_round_host_intros=None):
        self.rounds = rounds
        self.immunity_types = immunity_types
        self.config_mutations = config_mutations or []
        self.should_summarise_phase = should_summarise_phase
        self.discussion_round_host_intros = discussion_round_host_intros or []

    def phase_summary_string(self, cfg):
        round_summary = ''
        for round in self.rounds:
            round_summary += f"{round.display_name(cfg)} - {round.rules_description(cfg)}\n"
        return round_summary

    def phase_progress_string(self, cfg, current_index):
        current_index -= 1
        lines = []
        for i, round in enumerate(self.rounds):
            if i < current_index:
                prefix = "✓"
                suffix = ""
            elif i == current_index:
                prefix = "▶"
                suffix = "  [NOW]"
            else:
                prefix = " "
                suffix = ""

            line = f"  {prefix} {round.display_name(cfg)}{suffix}"
            
            # Inline rules for upcoming/current rounds only
            if i >= current_index:
                rules = round.rules_brief(cfg)
                if rules:
                    line += f"  — {rules}"
            
            lines.append(line)

        return "\n".join(lines)

    def detailed_rules_string(self, cfg, current_index):
        rules = []
        for i, round in enumerate(self.rounds):
            if i > current_index:
                if round.is_game() or round.is_vote():
                    rules.append(f"{round.display_name(cfg)} - {round.rules_description(cfg)}")
        if not rules:
            return ""
        return "\nUPCOMING GAME RULES:\n" + "\n".join(rules) + "\n"

    def phase_intro_string(self, phase_number, num_players, cfg):
        #this needs to move to the cfg file sadly enough. #TODO
        return None
        if num_players == 2:
            #not true for PD finale
            return f"Two players remain. Only one player will remain at the end of this phase. "
        else:
            return None
        #When we bring back immunities, we can look at this again
        phase_description = f"🚨 WELCOME PLAYERS, TO PHASE {phase_number} 🚨. "

        

        #--------------------

        phase_description += f"In this phase we will have: "

        discussion_rounds = [round for round in self.rounds if round.is_discussion()]
        if len(discussion_rounds) == 1:
            phase_description += "A discussion round. "
        elif len(discussion_rounds) > 1:
            phase_description += "Discussion rounds. "


        if any(round.is_game() for round in self.rounds):
            phase_description += "A Game Round. "

        has_elimination = any(round.is_vote() for round in self.rounds)
        if has_elimination:
            phase_description += "An Elimination. "


        if has_elimination and self.immunity_types:
            immunity_message = f"HOWEVER! This elimination round has the following immunities in play:\n"
            for immunity in self.immunity_types:
                immunity_message += f"- {immunity.display_name(cfg)}: {immunity.rules_description(cfg)}\n"
            phase_description += immunity_message


        return phase_description

