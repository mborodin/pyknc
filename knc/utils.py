import pexpect


device_password = 'admin'


def push_to_device(input_file, address, output_file):
    dev = pexpect.spawn('/usr/bin/scp %s root@%s:%s' %
                        (input_file, address, output_file))
    res = []
    try:
        dev.expect('password:')
        dev.sendline(device_password)
        res = dev.readlines()
    except pexpect.EOF:
        pass
    dev.close()
    return ''.join([i.decode(encoding='UTF-8') for i in res if i != b'\r\n'])


def run_on_device(command, device):
    dev = pexpect.spawn('/usr/bin/ssh root@%s %s' % (device, command))
    dev.expect('password:')
    dev.sendline(device_password)
    res = dev.readlines()
    dev.close()
    return ''.join([i.decode(encoding='UTF-8') for i in res if i != b'\r\n'])
