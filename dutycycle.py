# Copyright (C) 2023 Salvatore Sanfilippo <antirez@gmail.com>
# All Rights Reserved
#
# This code is released under the BSD 2 clause license.
# See the LICENSE file for more information

import time

# This class is used in order to track the duty cycle of the
# LoRa radio. Each time the TX is activated, we need to call
# the start_tx() method. When the TX ends we call end_tx().
# By doing so, we can use get_duty_cycle() to obtain a float
# number from to 0 to 100 expressing the percentage of time
# the TX was active.
#
# The algorithm divides the time in self.slots_num slots each
# of the duration of self.slots_dur seconds. They default to
# 4 slots of 15 minutes. Each slot knows the total tx time
# during that slot, in milliseconds. When we call get_duty_cycle()
# the class will perform the average of the slots.
class DutyCycle:
    def __init__(self,slots_num=4,slots_dur=60*15):
        self.slots_dur = slots_dur
        self.slots_num = slots_num
        # Allocate our slots. The txtime is the number of milliseconds
        # we transmitted during that slot. About 'epoch', see the
        # self.get_epoch() method for more info.
        self.slots = [{'txtime':0,'epoch':0} for i in range(self.slots_num)]
        self.tx_start_time = 0 # time.ticks_ms() of start_tx() call.

    #  Return the current active slot. This is just the UNIX time
    # divided by the slot duration, modulo the number of slots. So
    # every self.slots_dur seconds it will increment, then wrap
    # around (because of the modulo).
    def get_slot_index(self):
        return self.get_epoch() % self.slots_num

    # Get an integer that increments once every self.slots_dur. We
    # know if a given slot was incremented recently, or if at this point
    # it went out of the time window, just by checking the epoch associated
    # with the slot. Each time we increment a slot, we set the epoch,
    # and if the epoch changed, we reset the time counter.
    def get_epoch(self):
        return int(time.time()/self.slots_dur)

    def start_tx(self):
        self.tx_start_time = time.ticks_ms()

    def end_tx(self):
        txtime = time.ticks_diff(time.ticks_ms(),self.tx_start_time)
        idx = self.get_slot_index()
        epoch = self.get_epoch()
        slot = self.slots[idx]
        if slot['epoch'] != epoch:
            slot['epoch'] = epoch
            slot['txtime'] = 0
        slot['txtime'] += txtime

    def get_duty_cycle(self):
        txtime = 0
        epoch = self.get_epoch()
        for slot in self.slots:
            # Add the time of slots yet not out of scope
            if slot['epoch'] > epoch - self.slots_num:
                txtime += slot['txtime']
        return (txtime / (self.slots_dur*self.slots_num*1000)) * 100

if __name__ == "__main__":
    d = DutyCycle(slots_num=4,slots_dur=10)
    while True:
        d.start_tx()
        time.sleep(0.1)
        d.end_tx()
        time.sleep(.9)
        # Should converge to 10%
        print(d.get_duty_cycle())
