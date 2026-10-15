# Diagnostic pods that still need deleting

A diagnostic pod bills until it is DELETED; stopping it is not enough. The
background waiter that normally reaps one dies with the container, and the
container has restarted several times, so this file is the record that
survives. The hourly check's stray sweep is the backstop: anything listed
here that is still RUNNING should be dealt with as described.

## x4b5r05fv0vak4 - wallart-audit, launched 19:23 UTC 15 Oct, $0.32/hr

Duplicate audit at 609,478 panels, 40,000 probes, the first run of the
rewritten comparison stage (83018ca).

  log:    https://x4b5r05fv0vak4-8000.proxy.runpod.net/boot.log
  result: https://x4b5r05fv0vak4-8000.proxy.runpod.net/audit.json

Expect roughly 60-100 minutes of downloading (609k GETs on 160 threads),
then "hashed N, missed M", then "compared ... of 40000", then one line
starting AUDIT, then AUDIT_DONE or AUDIT_FAILED.

WHAT TO DO:
  * AUDIT_DONE      save audit.json to notes/audit_609478.json, commit it,
                    then DELETE the pod.
  * AUDIT_FAILED or AUDIT_UNRELIABLE
                    save the boot.log tail, DELETE the pod, and read it
                    before relaunching - AUDIT_UNRELIABLE means more than 5%
                    of panels would not download, which is a failure and not
                    a result.
  * still advancing after 2 hours
                    let it finish and say so.
  * not advancing   DELETE it.

Delete with:
  curl -sS -X DELETE -H "Authorization: Bearer $RUNPOD_API_KEY" \
       https://rest.runpod.io/v1/pods/x4b5r05fv0vak4
