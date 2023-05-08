# Gmail Automation

<hr>

### <b>Brief:</b>

1. Checks for new emails in a given Gmail ID.
2. Replies to emails that have no prior replies.
3. Adds a label to the replied email and moves the email to the label.
4. Repeats task in random intervals of 45 to 120 secs.
5. Ensure no double replies are sent to any email at any point of time.

<hr>

### <b>Requirement:</b>

1. Download the xml from this [link][link]
2. From the xml, please parse through to the first download link whose file_type is <i>DLTINS</i> and download the zip
3. Extract the xml from the zip.
4. Convert the contents of the xml into a CSV with the following header:
	- FinInstrmGnlAttrbts.Id
	- FinInstrmGnlAttrbts.FullNm
	- FinInstrmGnlAttrbts.ClssfctnTp
	- FinInstrmGnlAttrbts.CmmdtyDerivInd
	- FinInstrmGnlAttrbts.NtnlCcy
	- Issr
5. Store the csv from step 4) in an AWS S3 bucket
6. The above function should be run as an AWS Lambda (Optional)

<hr>
