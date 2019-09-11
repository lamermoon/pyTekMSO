import pyTekMSO

ACQ_N = 5

print('Connecting to scope...')
scope = pyTekMSO.TekMSO('141.83.62.51')

print('Setting FastFrame count to max', end='')
scope.set_fastframe_count_to_max()
print(' (', scope.get_fastframe_count(), ')')


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

print('\nDone.')
