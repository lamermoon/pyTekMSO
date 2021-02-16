import visa
from enum import Enum
from pyTekMSO.pyTekMSOConst import *

class Acq_Mode(Enum):
    RUNSTOP = False
    SEQUENCE = True
    pass

class Source_Type(Enum):
    CH = 'CH'
    MATH = 'MATH'
    REF = 'REF'
    ALL = 'ALL'
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

    #adds literal quotes at start and end of plainStr if they are not there yet, see qstring format in manual
    def _check_and_fix_qstring(self,plainStr):
        if plainStr[0] != "\"":
            plainStr = "\""+plainStr
        if plainStr[len(plainStr)-1] != "\"":
            plainStr = plainStr + "\""
        return plainStr
    
    # General query    
    def get(self, attr, dbg=False):
        return self._query(str(attr) + '?', dbg=dbg)

    def set(self, attr, val, dbg=False):
        return self._write(' '.join([str(attr), str(val)]), dbg=dbg)

    
    ###############################
    ## Methods ordered by groups ##
    ###############################

    #Filesystem Command Group

    def set_mkdir(self,path):
        """Creates directory, no error check"""
        path = self._check_and_fix_qstring(path)
        self.set('FILESystem:MKDir',path)
        return 

    def set_cwd(self,path):
        """Sets current working directory"""
        path = self._check_and_fix_qstring(path)
        self.set('FILESystem:CWD', path)
        return
    
    def get_cwd(self):
        """Returns current working directory"""
        return self.get('FILESystem:CWD')
    
    def get_ldir(self):
        """List content of current working directory. Empty dir returns literal \"\", not empty string"""
        return self.get('FILESystem:LDIR')

    # Sync commands

    def get_busy(self):
        return int(self.get('BUSY'))

    def set_cls(self):
        self.set('*CLS','')
        return

    def setup_opc(self):
        """Enables operation complete message"""
        self.set('DESE','1')
        self.set('*ESE', '1')
        self.set('*SRE 0','1')
        return

    def get_trigger_state(self):
        """get trigger state, returns strings"""
        return self.get('TRIGger:STATE')

    def set_opc(self):
        """Request generation of operation complete message once all async ops are done"""
        self._write('*OPC')
        return

    def get_esr(self):
        """query esr register, usefull for busy wait on operation complete message"""
        return int(self._inst.query('*ESR?'))


    # Acquisition Command Group


    def get_acq_seq_current(self):
        """Get num of aquisitions in measurement"""
        return int(self.get('ACQuire:SEQuence:CURrent'))

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

    def get_horizontal_samplerate(self):
        """Get Samplerate"""
        return self.get('HORizontal:MODE:SAMPLERate')

    def get_horizontal_length(self):
        """Get length of trace"""
        return self.get('HORizontal:MODE:RECOrdlength')

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

    def get_horizontal(self):
        return self.get('HORizontal')


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
    def reset_setup(self):
        """Reset the setup configuration"""
        self.set(LOAD_SETUP, FACTORY_SETUP)
        return
        
    def load_setup(self, filename, path):
        """Load a setup configuration file"""
        if filename[-4:] != '.set':
            filename += '.set'
            pass
        path = self._check_and_fix_qstring(path) 
        self.set(LOAD_SETUP, path, dbg=True)
        return
    

    def save_setup(self, filename, path):
        """Save the current setup"""
        if filename[-4:] != '.set':
            filename += '.set'
            pass
        path = self._check_and_fix_qstring(path)
        self.set(SAVE_SETUP, path)
        return

    def enable_save_setup_includerefs(self):
        """Enable including reference waveforms when saving setup"""
        self.set(SAVE_SETUP_INCLUDEREFS, ON)
        return
    
    def disable_save_setup_includerefs(self):
        """Disable including reference waveforms when saving setup"""
        self.set(SAVE_SETUP_INCLUDEREFS, OFF)
        return
    
    
    # SaveOn Command Group
    def enable_save_on_trigger(self):
        """Enable SaveOn Trigger mode"""
        self.set(SAVEON_TRIGGER, ON)
        return

    def disable_save_on_trigger(self):
        """Disable SaveOn trigger mode"""
        self._inst.write(SAVEON_TRIGGER, OFF)
        return

    def get_save_on_trigger_mode(self):
        """Return whether SaveOn is enabled or not"""
        return (self.get(SAVEON_TRIGGER) == '1')

    def get_save_on_trigger_file_path(self):
        """Returns the path files are saved to when SaveOn is enabled"""
        return self.get(SAVEON_TRIGGER_FILE_PATH)

    def set_save_on_trigger_file_path(self, path):
        """Set the absolute path to save files to when SaveOn is enabled"""
        path = self._check_and_fix_qstring(path)
        self.set('SAVEON:FILE:DEST', path)
        return


    def get_save_on_trigger_file_name(self):
        """Returns the filename of files saved due to SaveOn trigger events"""
        return self.get(SAVEON_TRIGGER_FILE_NAME)

    def set_save_on_trigger_file_name(self, filename):
        """Set the filename of files saved due to SaveOn trigger events"""
        self.set(SAVEON_TRIGGER_FILE_NAME, filename)
        return

    def enable_save_waveform_on_trigger(self):
        """Enable Waveform saving on trigger"""
        self.get(SAVE_WAVEFORM_ON_TRIGGER, ON)
        return

    def disable_save_waveform_on_trigger(self):
        """Disable Waveform saving on trigger"""
        self.get(SAVE_WAVEFORM_ON_TRIGGER, OFF)
        return

    def isset_save_waveform_on_trigger(self):
        """Return whether Waveforms are saved on trigger"""
        return self.get(SAVE_WAVEFORM_ON_TRIGGER)

    def get_save_on_trigger_set_save_on_trigger_file_pathwaveform_source(self):
        """Get the source of the waveform saved on trigger"""
        return self.get(SAVEON_TRIGGER_WAVEFORM_SOURCE)

    def set_save_on_trigger_waveform_source(self, src_type, src_idx):
        """Set the source of the waveform saved on trigger"""
        if src_type == Source_Type.ALL:
            self.set(SAVEON_TRIGGER_WAVEFORM_SOURCE, str(src_type))
            pass
        else:
            self.set(SAVEON_TRIGGER_WAVEFORM_SOURCE, ''.join([str(src_type),str(int(src_idx))]))
            pass
        return
    
    
    pass # End MSO6 Class
