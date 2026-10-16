# Diagnostic pods that still need deleting

A diagnostic pod bills until it is DELETED; stopping it is not enough. The
background waiter that normally reaps one dies with the container, and the
container has restarted several times, so this file is the record that
survives. The hourly check's stray sweep is the backstop: anything listed
here that is still RUNNING should be dealt with as described.

## DONE - x4b5r05fv0vak4, wallart-audit, 19:23-20:32 UTC 15 Oct, $0.32/hr

AUDIT_DONE at 20:32:42. Result in notes/audit_611441.json, pod deleted,
confirmed gone from the pod list. Nothing outstanding.

Original entry:

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

## dcw129pdyp2dwf - wallart-sweep, launched 21:16 UTC 15 Oct, $0.17/hr

Text sweep CALIBRATION run: 1,500 of the 35,925 pre-11-Oct-22:00 panels,
measuring how many carry a clipped-letter sliver along the bottom edge.
Its launcher reaps it in a finally, but a container restart kills the
launcher, which is how a pod leaks.

  log:    https://dcw129pdyp2dwf-8000.proxy.runpod.net/boot.log
  result: https://dcw129pdyp2dwf-8000.proxy.runpod.net/sweep.json
  sheet:  https://dcw129pdyp2dwf-8000.proxy.runpod.net/sheet.jpg

Prints SWEEP_DONE or SWEEP_FAILED. Expect a few minutes to install easyocr
and fetch its models, then "examined N" every 200 panels, then one SWEEP
line. 1,500 panels is well under ten minutes of work.

WHAT TO DO: save sweep.json and sheet.jpg, then DELETE the pod. If it is
still RUNNING with no progress line advancing, delete it.

  curl -sS -X DELETE -H "Authorization: Bearer $RUNPOD_API_KEY" \
       https://rest.runpod.io/v1/pods/dcw129pdyp2dwf

## 16 Oct 14:02 UTC - THE RUN STOPPED: account balance exhausted

All twelve shards were terminated by RunPod inside about two minutes.
The watchdog saw them generating at 14:01:48 and saw none at 14:03:49,
having itself killed only three all window, hours apart, on their normal
ten-hour clocks. Nothing here did this.

The create API says it plainly:

    "create pod: Your account balance is too low to rent a pod."

Probed across tiers: community A4500, community RTX 4000 Ada and CPU all
return the balance error; community 3090 and all three SECURE types
return "no instances currently available", which is ordinary capacity
and not the cause. The balance is the cause.

NOTHING IS LOST. Every panel is in R2 - 734,760 of them, 2,939,040
listings - and the buckets are the bookmark. gen_gated.py --resume lists
them and skips what is done, so the run continues from where it stopped
the moment there is credit.

WHAT IS NEEDED: about $102 to finish all five million, being $79.52 of
GPU for the remaining 225,240 panels, $22.28 for the CPU listing stage
and $0.09 for the owed text sweep. $100 is marginally short; $110 to
$120 covers it with room for the card prices moving.

The shard filler is deliberately left running. It retries every 45
seconds, each attempt is a rejected API call that costs nothing, and it
means the fleet refills by itself within a minute of a top-up landing
rather than waiting for the next hourly check.
