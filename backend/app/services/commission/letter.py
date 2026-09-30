"""Письмо менеджерам о новой заявке кандидата в конкурсную комиссию."""

from html import escape

from app.config import get_settings
from app.models.commission import CommissionApplication
from app.services.experts.catalog import OBJECT_BY_CODE
from app.services.mail.sender import send_email


def attestation_lines(application: CommissionApplication) -> list[str]:
    """Аттестации строками вида «Э1 КЛ/ТП, 1 категория»."""

    lines = []
    for item in application.attestations:
        known = OBJECT_BY_CODE.get(item["object_code"])
        label = known.label if known else item["object_code"]
        lines.append(f"{item['area_code']} {label}, {item['category']} категория")

    return lines


def build_text(application: CommissionApplication) -> str:
    """Текстовая версия письма."""

    attestations = "\n".join(f"— {line}" for line in attestation_lines(application))
    created = application.created_at.strftime("%d.%m.%Y %H:%M")

    return (
        "Новая заявка в конкурсную комиссию\n\n"
        f"ФИО: {application.full_name}\n"
        f"Аттестация:\n{attestations}\n"
        f"Дата: {created}"
    )


def build_html(application: CommissionApplication) -> str:
    """HTML-версия письма в том же оформлении, что и заявки с сайта."""

    attestations = "<br>".join(escape(line) for line in attestation_lines(application))
    fields = [
        ("ФИО", escape(application.full_name)),
        ("Аттестация", attestations),
        ("Дата", application.created_at.strftime("%d.%m.%Y %H:%M")),
    ]

    rows = "".join(
        f"""
        <tr>
          <td style="padding:10px 16px;color:#7b8190;font-size:13px;
                     border-bottom:1px solid #eceef3;white-space:nowrap;
                     vertical-align:top;">{label}</td>
          <td style="padding:10px 16px;color:#0b0b0b;font-size:14px;
                     border-bottom:1px solid #eceef3;">{value}</td>
        </tr>
        """
        for label, value in fields
    )

    return f"""
    <html>
      <body style="margin:0;padding:24px;background:#f5f6f8;
                   font-family:Arial,Helvetica,sans-serif;">
        <table style="max-width:640px;margin:0 auto;width:100%;
                      border-collapse:collapse;background:#fff;
                      border-radius:12px;overflow:hidden;">
          <tr>
            <td colspan="2" style="padding:20px 16px;background:#f69827;
                                   color:#fff;font-size:18px;font-weight:bold;">
              Заявка №{application.id} в конкурсную комиссию
            </td>
          </tr>
          {rows}
        </table>
      </body>
    </html>
    """


async def send_commission_letter(application: CommissionApplication) -> None:
    """Отправить менеджерам письмо о заявке кандидата. Адреса — из NOTIFY_EMAILS."""

    settings = get_settings()

    await send_email(
        recipients=settings.notify_emails,
        subject=f"Конкурсная комиссия: заявка №{application.id} — {application.full_name}",
        text=build_text(application),
        html=build_html(application),
    )
