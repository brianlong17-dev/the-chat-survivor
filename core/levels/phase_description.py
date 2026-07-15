class PhaseDescription:
    def __init__(self, rounds=None,config_mutations=None, should_summarise_phase=True):
        self.rounds = rounds
        self.config_mutations = config_mutations or []
        self.should_summarise_phase = should_summarise_phase

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
