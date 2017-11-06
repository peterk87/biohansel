from bio_hansel.quality_check.quality_check_functions import does_subtype_result_exist, check_min_tiles_reached, \
    check_is_confident_subtype
from bio_hansel.quality_check.const import PASS_MESSAGE, FAIL_MESSAGE, WARNING_MESSAGE
from bio_hansel.subtype import Subtype


QC_FUNCS = [
    check_is_confident_subtype,
    check_min_tiles_reached
]


def perform_quality_check(st: Subtype):
    overall_qc_status = 'PASS'
    messages = []

    if does_subtype_result_exist(st) is False:
        st.qc_status = 'FAIL'
        st.qc_message = 'FAIL: No matching tiles exist, quality checking was not run.'
        return None

    for func in QC_FUNCS:
        status, message = func(st)
        if status is PASS_MESSAGE:
            # If quality check function passes, move on to the next.
            continue
        messages.append('{}: {}'.format(status, message))
        if status is FAIL_MESSAGE:
            overall_qc_status = 'FAIL'
        elif status == WARNING_MESSAGE:
            overall_qc_status = 'WARNING'

    st.qc_status = overall_qc_status
    st.qc_message = ' | '.join(messages)
