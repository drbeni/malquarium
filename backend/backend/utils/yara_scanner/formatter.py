def format_malice(match):
    return "{}".format(match.rule if not (match.rule.startswith("_")
                                          or match.rule.startswith('PEiD'))
                       else
                       match.meta.get('description', '<None>')
                       .split(' -> ')[0]
                       .split(' --> ')[0]
                       .replace("[", "")
                       .replace("]", ""))
