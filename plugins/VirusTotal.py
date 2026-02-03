import hashlib
import time

import requests
from taiiwobot.plugin import Plugin


class VirusTotal(Plugin):
    def __init__(self, bot):
        self.bot = bot
        if "virustotal_key" not in self.bot.config:
            print(
                'VirusTotal API key not specified. Add `"virustotal_key": "<your key>",` to your config file.'
            )
            return None
        self.api_key = self.bot.config["virustotal_key"]

        @bot.on("message", self.name)
        def scan_attachments(message):
            if getattr(message, "author", None) == self.bot.server.me():
                return
            attachments = getattr(message, "attachments", None) or []
            if not attachments:
                return
            for attachment in attachments:
                self.bot.util.thread(self.scan_attachment, (message, attachment))

    def scan_attachment(self, message, attachment):
        try:
            report = self.fetch_report(message, attachment)
        except self.bot.util.RuntimeError:
            return
        response = "VirusTotal report for %s: %s" % (
            getattr(attachment, "filename", "attachment"),
            report["permalink"],
        )
        if report["embed"]:
            self.bot.msg(
                message.target,
                response,
                embed=report["embed"],
                follows=message,
            )
        else:
            self.bot.msg(message.target, response, follows=message)

    def fetch_report(self, message, attachment):
        attachment_data = self.download_attachment(message, attachment)
        file_hash = hashlib.sha256(attachment_data).hexdigest()
        report = self.request_report(message, file_hash)
        if report.get("response_code") == 1:
            return self.format_report(report)
        self.upload_file(message, attachment, attachment_data)
        report = self.poll_report(message, file_hash)
        return self.format_report(report)

    def download_attachment(self, message, attachment):
        url = getattr(attachment, "url", None)
        if not url and isinstance(attachment, dict):
            url = attachment.get("url")
        if not url:
            raise self.bot.util.RuntimeError(
                "VirusTotal: attachment URL not available", message.target, self
            )
        try:
            response = requests.get(url, timeout=30)
        except requests.RequestException:
            raise self.bot.util.RuntimeError(
                "VirusTotal: failed to download attachment", message.target, self
            )
        if response.status_code != 200:
            raise self.bot.util.RuntimeError(
                "VirusTotal: failed to download attachment", message.target, self
            )
        return response.content

    def request_report(self, message, file_hash):
        try:
            response = requests.get(
                "https://www.virustotal.com/vtapi/v2/file/report",
                params={"apikey": self.api_key, "resource": file_hash},
                timeout=30,
            )
        except requests.RequestException:
            raise self.bot.util.RuntimeError(
                "VirusTotal: failed to fetch report", message.target, self
            )
        if response.status_code != 200:
            raise self.bot.util.RuntimeError(
                "VirusTotal: failed to fetch report", message.target, self
            )
        try:
            return response.json()
        except ValueError:
            raise self.bot.util.RuntimeError(
                "VirusTotal: invalid report response", message.target, self
            )

    def upload_file(self, message, attachment, attachment_data):
        filename = getattr(attachment, "filename", "attachment")
        if isinstance(attachment, dict):
            filename = attachment.get("filename", filename)
        files = {"file": (filename, attachment_data)}
        try:
            response = requests.post(
                "https://www.virustotal.com/vtapi/v2/file/scan",
                files=files,
                data={"apikey": self.api_key},
                timeout=60,
            )
        except requests.RequestException:
            raise self.bot.util.RuntimeError(
                "VirusTotal: failed to submit file for scanning",
                message.target,
                self,
            )
        if response.status_code != 200:
            raise self.bot.util.RuntimeError(
                "VirusTotal: failed to submit file for scanning",
                message.target,
                self,
            )

    def poll_report(self, message, file_hash):
        for _ in range(5):
            time.sleep(5)
            report = self.request_report(message, file_hash)
            if report.get("response_code") == 1:
                return report
        raise self.bot.util.RuntimeError(
            "VirusTotal: report is not ready yet", message.target, self
        )

    def format_report(self, report):
        positives = report.get("positives")
        total = report.get("total")
        scan_date = report.get("scan_date")
        permalink = report.get("permalink")
        fields = []
        if positives is not None and total is not None:
            fields.append(["Detections", "%s / %s" % (positives, total), True])
        if scan_date:
            fields.append(["Scan date", scan_date, True])
        embed = None
        if hasattr(self.bot.server, "embed"):
            embed = self.bot.server.embed(
                title="VirusTotal scan result",
                url=permalink,
                fields=fields,
            )
        return {"permalink": permalink or "No report link", "embed": embed}
