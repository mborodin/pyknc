from knc.PMBus import PMBus
from knc.device import ASICBoard

make_pep8_happy = PMBus
make_pep8_happy = ASICBoard

import platform
if platform.machine() != 'armv7l':
    from knc.utils import push_to_device, run_on_device
    make_pep8_happy = push_to_device
    make_pep8_happy = run_on_device
