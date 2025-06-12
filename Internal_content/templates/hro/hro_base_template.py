from Utils.configuration_management import Configuration

Configuration.Knobs.Config.core_count.set_value(1)
Configuration.Knobs.Template.scenario_count.set_value(1)
Configuration.Knobs.Template.scenario_query.set_value({Configuration.Tag.HRO: 100, Configuration.Tag.REST: 1})