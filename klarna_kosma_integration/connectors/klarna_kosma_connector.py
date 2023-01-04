# Copyright (c) 2022, ALYF GmbH and contributors
# For license information, please see license.txt
from typing import Dict
import frappe
import requests

from frappe import _
from frappe.utils import add_days, add_to_date, formatdate, get_datetime, nowdate
from erpnext.accounts.utils import get_fiscal_year

from klarna_kosma_integration.connectors.klarna_kosma_consent import (
	KlarnaKosmaConsent,
)
from klarna_kosma_integration.connectors.klarna_kosma_flow import (
	KlarnaKosmaFlow,
)
from klarna_kosma_integration.connectors.kosma_session import KosmaSession


class KlarnaKosmaConnector:
	def __init__(self, config: Dict = None) -> None:
		env = config.env
		is_playground = "playground." if env == "Playground" else ""
		kosma_domain = f"api.openbanking.{is_playground}klarna.com"

		self.api_token = config.api_token
		self.psu = (
			{  # TODO: fetch public IP, user agent
				"user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
				"ip_address": "49.36.101.156",
			},
		)
		self.base_url = f"https://{kosma_domain}/xs2a/v1/sessions/"
		self.base_consent_url = f"https://{kosma_domain}/xs2a/v1/consents/"

		self.get_headers = (self._get_headers,)
		self.get_date_range = (self._get_session_flow_date_range,)

		self.access.update(config)

	def _get_headers(self, content_type: str = None):
		return {
			"Content-Type": content_type or "application/json",
			"Authorization": "Token {0}".format(self.api_token),
		}

	def _get_session_flow_date_range(self, is_flow: bool = False):
		# TODO: verify logic
		current_fiscal_year = get_fiscal_year(nowdate(), as_dict=True)
		start_date = current_fiscal_year.year_start_date
		return {
			"from_date": formatdate(start_date, "YYYY-MM-dd"),
			"to_date": nowdate() if is_flow else add_days(nowdate(), 90),
		}
