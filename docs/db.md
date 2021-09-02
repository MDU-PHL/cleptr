# Proposed DB schema for cleptr

Due to NFS limitations this structure will be set up as a simple file based organisation, rather than a true DB. However, with the view to having this as an actual DB in the future, some though has gone into how to tructure and represent the relationships.
## Sample table

Table of samples and sample information.

Seq_ID: unique sequence ID,
Date_added: date added to DB,
Cluster : {current: date_1,
            date_1: cgtX,
            date_2: cgtY},
Serovar: serovar (if available),
ST: mlst (if available),
Database: Name of cgMLST database used to generate clusters


## Cluster table

This table keeps the CURRENT status of clusters

cgtX: {current : date_1,
        date_1: [samples in cluster],
        date_2: [samples in cluster]}

## NEPPS view

This is only for Salmonella and Listeria. This database view provides metadata (state, postcode, 2x2 code) for all samples for which results CAN be communicated to DH and AT. CIC samples are NOT in this view.
