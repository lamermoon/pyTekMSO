import pyTekMSO

ACQ_N = 3

print('Connecting to scope...')
scope = pyTekMSO.TekMSO('141.83.62.51')
scope.disable_header()

print('Loading Tim_BA.set setting')
scope.load_setup('Tim_BA.set')
print('Setting FastFrame count to max', end='')
#scope.set_fastframe_count_to_max()
scope.set_fastframe_count(5)
print(' (', scope.get_fastframe_count_max(), ')')


for i in range(ACQ_N):
    print('Running acquisition [', i+1, '/', ACQ_N, ']', end='\r')
    scope.enable_fastframe()
    scope.enable_save_on_trigger()
    scope.start_sequence_acq()
    # Run application here

    # END Run application here
    while scope.get_acq_state() != 0:
        pass
    pass

scope.reset_setup()

print('\nDone.')
