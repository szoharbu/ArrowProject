
from Arrow.Utils.configuration_management import Configuration

Configuration.Knobs.Config.core_count.set_value(2)
Configuration.Knobs.Template.scenario_count.set_value(5)
Configuration.Knobs.Template.scenario_query.set_value({Configuration.Tag.DISPATCH:80,
                                                       Configuration.Tag.BRANCH:10,
                                                       "bypass_bursts":10,
                                                       Configuration.Tag.REST:1})
