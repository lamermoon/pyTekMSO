import visa
from enum import Enum
from pyTekMSO.pyTekMSOConst import *

class Acq_Mode(Enum):
    RUNSTOP = False
    SEQUENCE = True
    pass

class TekMSO_Error(Exception):
    def __init__(self, msg):
        self.msg = msg
        pass
    def __repr__(self):
        return self.msg
    def __str__(self):
        return self.msg
    pass

class TekMSO(object):

    def __init__(self, device_ip):
        self._MSO_RESOURCE_STR = '::'.join(['TCPIP', device_ip, 'INSTR'])
        self._rm = visa.ResourceManager('@py')
        self._inst = self._rm.open_resource(self._MSO_RESOURCE_STR, read_termination='\n', write_termination='\n')
        return

    def __repr__(self):
        return self._inst.query('*IDN?')

    def __str__(self):
        return self._inst.query('*IDN?')


    def _concat_commands(self, command_list):
        return ';'.join(command_list)

    def _query(self, cmd, dbg=False):
        if dbg:
            print('[DBG] Query:', cmd)
            pass
        ans = self._inst.query(cmd)
        if dbg:
            print('[DBG] Answr:', ans)
            pass
        return ans
    
    def _write(self, cmd, dbg=False):
        if dbg:
            print('[DBG] Write:', cmd)
            pass
        return self._inst.write(cmd)

    
    # General query    
    def get(self, attr, dbg=False):
        return self._query(str(attr) + '?', dbg=dbg)

    def set(self, attr, val, dbg=False):
        return self._write(' '.join([str(attr), str(val)]), dbg=dbg)

    
    ###############################
    ## Methods ordered by groups ##
    ###############################

    # Acquisition Command Group
    def get_acq_state(self):
        """Get acquisition state"""
        return int(self.get(ACQ_STATE))
    
    def start_acq(self):
        """Start acquisition"""
        self.set(ACQ_STATE, ON)
        return
    
    def stop_acq(self):
        """Stop acquisition"""
        self.set(ACQ_STATE, OFF)
        return

    def start_sequence_acq(self):
        self.enable_acq_mode_sequence()
        self.start_acq()
        return
    
    def start_runstop_acq(self):
        self.enable_acq_mode_runstop()
        self.start_acq()
        return
    
    def get_acq_mode(self):
        """Get acquisition mode"""
        return self.get(ACQ_MODE)

    def set_acq_mode(self, mode):
        """Set acquisition mode"""
        if mode == Acq_Mode.RUNSTOP:
            self.set(ACQ_MODE, ACQ_MODE_RUNSTOP)
            return
        else:
            self.set(ACQ_MODE, ACQ_MODE_SEQUENCE)
            return
        return

    def enable_acq_mode_runstop(self):
        """Enable acquisition mode Run/Stop"""
        self.set_acq_mode(Acq_Mode.RUNSTOP)
        return

    def enable_acq_mode_sequence(self):
        """Enable acquisition mode Sequence/Single"""
        self.set_acq_mode(Acq_Mode.SEQUENCE)
        return


    # Horizontal Command Group
    def enable_fastframe(self):
        """Enable FastFrame mode"""
        self.set(FASTFRAME_STATE, ON)
        return

    def disable_fastframe(self):
        """Disable FastFrame mode"""
        self.set(FASTFRAME_STATE, OFF)
        return

    def get_fastframe_count_max(self):
        """Get max possible FastFrame count"""
        return int(self.get(FASTFRAME_COUNT_MAX))

    def get_fastframe_count(self):
        """Get configured FastFrame count"""
        return int(self.get(FASTFRAME_COUNT))
    
    def set_fastframe_count(self, x):
        """Set FastFrame count"""
        self.set(FASTFRAME_COUNT, x)
        return

    def set_fastframe_count_to_max(self):
        """Set FastFrame count to max possible value"""
        self.set_fastframe_count(self.get_fastframe_count_max())
        return


    # Miscellaneous Command Group
    def get_header_mode(self):
        """Get header mode"""
        return self.get(HEADER)
    
    def set_header_mode(self, state):
        """Set header mode"""
        if state:
            self.set(HEADER, ON)
            return
        else:
            self.set(HEADER, OFF)
            return
        return
    
    def enable_header(self):
        """Enable header"""
        self.set_header_mode(1)
        return
    
    def disable_header(self):
        """Disable header"""
        self.set_header_mode(0)
        return

    
    # Save and Recall Command Group
    def enable_save_on_trigger(self):
        """Enable SaveOn Trigger mode"""
        self.set(SAVEON_TRIGGER, ON)
        return

    def disable_save_on_trigger(self):
        """Disable SaveOn trigger mode"""
        self._inst.write(SAVEON_TRIGGER, OFF)
        return

    def get_save_on_trigger_mode(self):
        return self.get(SAVEON_TRIGGER)

    def enable_save_waveform_on_trigger(self):
        self.get(SAVE_WAVEFORM_ON_TRIGGER, ON)
        return

    def disable_save_waveform_on_trigger(self):
        self.get(SAVE_WAVEFORM_ON_TRIGGER, OFF)
        return

    def isset_save_waveform_on_trigger(self):
        return self.get(SAVE_WAVEFORM_ON_TRIGGER)
    
    pass # End MSO6 Class
