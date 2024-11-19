shopt -s nullglob

#--------------------------------------------------------------------
#                           Feedback
#--------------------------------------------------------------------
safe_echo() { printf -- "[$(date --rfc-3339=seconds)] %b" "${1//%/%%}"; }
m_die()     { safe_echo "[ERROR] ${*} Exiting.\n"; exit 1; }
m_error()   { safe_echo "[ERROR] ${*}\n"; }
m_info()    { safe_echo "[INFO] ${*}\n"; }

#--------------------------------------------------------------------
#                             Email
#--------------------------------------------------------------------

# Define E-Mail content
get_mime_content()
{
    local removed_files
    local nl="
"
    mime_from="From: no-reply@mercedes-benz.com"
    mime_recipients="To: ${mime_recipients}"
    mime_cc="Cc: ${mime_cc}"
    mime_subject="Subject: [FDC] failed download for ${fdc_config_name} on $(hostname)"
    mime_boundary=$(uuidgen)
    mime_boundary2=$(uuidgen)

    mime_text="Dear Madam or Sir,

Attached is the log file for the failed fdc download for the configuration ${fdc_config_name}:
${fdc_log}

Regards,
AS-PLM Betrieb

AS-PLM Application Services
Systems Integration
GDU AMI | GDC PLM | Product Lifecycle Services

#####This is an automatically generated E-Mail.####"

    mime_html="<!doctype html>
<html><head><meta charset="utf-8"></head>
<body><p>Dear Madam or Sir,<br></p>
<p>Attached is the log file for the failed fdc download for the configuration:</p>
<pre>${fdc_log}</pre>
<p>Regards,<br>AS-PLM Betrieb<br></p>
<span style='font-size:8.0pt;font-family:"Calibri",sans-serif;'>
<p><b>AS-PLM Application Services</b><br>Systems Integration
<br>GDU AMI | GDC PLM | Product Lifecycle Services<br>
<br><b>#####This is an automatically generated E-Mail.####</b></p>
</span></body></html>"
}

# Send a Multipurpose Internet Mail Extensions E-Mail.
# https://en.wikipedia.org/wiki/MIME
send_mime_mail()
{
    emailfile="/var/tmp/${script_name}.${$}.eml"
    get_mime_content "${*}"
    m_info "Sending E-Mail $mime_recipients with $mime_cc"

cat << EOM > "$emailfile"
$mime_from
$mime_recipients
$mime_cc
Reply-To: as-plm.betrieb@mercedes-benz.com
$mime_subject
Return-Path: as-plm.betrieb@mercedes-benz.com
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary=$mime_boundary

This is a message with multiple parts in MIME format

--$mime_boundary
Content-Type: multipart/alternative; boundary=$mime_boundary2

--$mime_boundary2
Content-Type: text/plain; charset="utf-8"
Content-Transfer-Encoding: quoted-printable
Content-Disposition: inline

$mime_text
--$mime_boundary2
Content-Type: text/html; charset="utf-8"
Content-Transfer-Encoding: quoted-printable
Content-Disposition: inline

$mime_html
--$mime_boundary2--
EOM

    # Encode attachments.

    filename="${fdc_log}"
    echo "${nl}--$mime_boundary" >> "$emailfile"
    echo "${nl}Content-Transfer-Encoding: base64" >> "$emailfile"
    echo "${nl}Content-Type: application/octet-stream; name=$filename" >> "$emailfile"
    echo "${nl}${nl}" >> "$emailfile"
    base64 $attachment >> "$emailfile"
    echo "${nl}" >> "$emailfile"
  
    echo "--$mime_boundary--" >> "$emailfile"

    /usr/sbin/sendmail -t < "$emailfile"
    rm "$emailfile"
}

#--------------------------------------------------------------------
#                             Main
#--------------------------------------------------------------------

# Prints help for the script
usage()
{
echo -n "Usage: $0 [options]

 Options:
  -c --fdc_config		fdc config name
  -l --fdc_log 			fdc log file
  -h, --help        Display this help and exit
  -m, --mail        Search for files and define e-mail recipients file

 Example:

  $0 --fdc_config xxx --fdc_log xxx.log --mail /applications/local/config/mail/cdmimporter_maillist.txt

"
}


sendFdcMail()
{
  lockfile="/var/tmp/$(basename $0).lockfile"

  # Check if this script is already running.
  exec 201<>"$lockfile"
  if flock -n 201; then
    trap 'rm -f $lockfile' INT TERM EXIT
    echo $$ 1>&201
  else
    read -r pid<&201
    m_die "Another instance of this script is already running with PID ${pid}."
  fi

  [[ -r "$recipients_file" ]] || m_die "Cannot open $recipients_file"
  mime_recipients=$(sed -n 's:^to_addresses[[:blank:]]*=[[:blank:]]*::p' $recipients_file | head -1 | tr -d '\r')
  mime_cc=$(sed -n 's:^cc_addresses[[:blank:]]*=[[:blank:]]*::p' $recipients_file | head -1 | tr -d '\r')
  [[ -z "$mime_recipients" && -z "$mime_cc" ]] && m_die "Please provide at least one e-mail address."

  [[ -r "$fdc_log" ]] || m_die "Cannot open $fdc_log"
  
  send_mime_mail

  ELAPSED="Elapsed time: $(($SECONDS / 3600))hrs $((($SECONDS / 60) % 60))min $(($SECONDS % 60))sec"
  m_info "$ELAPSED"
  m_info "Script execution finished."
}

# Read the arguments and do stuff
if (($#)); then
  for arg in "$@"
    do
      case "$arg" in
	    -c|--fdc_config)
		  shift
		  if [[ "$1" ]]; then
            fdc_config_name=${1}
          else
            m_die "Please provide an fdc config name."
          fi
		  ;;
		$fdc_config_name)
          continue
          ;;
		-l|--fdc_log)
		  shift
		  if [[ "$2" ]]; then
            fdc_log=${2}
          else
            m_die "Please provide an fdc log file path."
          fi
		  ;;
		$fdc_log)
          continue
          ;;
        -m|--mail)
          shift
          if [[ "$3" ]]; then
            recipients_file=${3}
          else
            m_die "Please provide a recipients file."
          fi
          sendFdcMail
          ;;
        $recipients_file)
          continue
          ;;
        -h|--help|help)
          usage
          ;;
        *)
          m_error "Invalid Option"
          ;;
      esac
    done
else
  usage
fi