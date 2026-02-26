from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings


def send_email(to_email: str, subject: str, html_content: str):
    """Envoie un email via SendGrid."""
    try:
        message = Mail(
            from_email=settings.DEFAULT_FROM_EMAIL,
            to_emails=to_email,
            subject=subject,
            html_content=html_content,
        )
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        sg.send(message)
        return True
    except Exception as e:
        print(f"Erreur email: {e}")
        return False


def send_order_confirmation(user_email: str, user_name: str, order_id: int,
                             event_title: str, quantity: int, total_price: float):
    """Email de confirmation de commande."""
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: #4f46e5; padding: 30px; text-align: center;">
            <h1 style="color: white; margin: 0;">HotelMate</h1>
        </div>
        <div style="padding: 30px; background: #f8fafc;">
            <h2 style="color: #1e293b;">Réservation confirmée ! 🎉</h2>
            <p style="color: #64748b;">Bonjour <strong>{user_name}</strong>,</p>
            <p style="color: #64748b;">Votre réservation a été créée avec succès.</p>

            <div style="background: white; border-radius: 12px; padding: 20px; margin: 20px 0;">
                <h3 style="color: #1e293b; margin-top: 0;">Détails de la commande</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 8px 0; color: #64748b;">Numéro de commande</td>
                        <td style="padding: 8px 0; font-weight: bold; color: #1e293b;">#{order_id}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; color: #64748b;">Événement</td>
                        <td style="padding: 8px 0; font-weight: bold; color: #1e293b;">{event_title}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; color: #64748b;">Nombre de billets</td>
                        <td style="padding: 8px 0; font-weight: bold; color: #1e293b;">{quantity}</td>
                    </tr>
                    <tr style="border-top: 1px solid #e2e8f0;">
                        <td style="padding: 12px 0; color: #1e293b; font-weight: bold;">Total payé</td>
                        <td style="padding: 12px 0; font-weight: bold; color: #4f46e5; font-size: 18px;">
                            {total_price} TND
                        </td>
                    </tr>
                </table>
            </div>

            <p style="color: #64748b;">Merci de votre confiance.</p>
            <p style="color: #64748b;">L'équipe HotelMate</p>
        </div>
    </div>
    """
    return send_email(user_email, f'Confirmation de réservation #{order_id}', html)


def send_welcome_email(user_email: str, user_name: str):
    """Email de bienvenue."""
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: #4f46e5; padding: 30px; text-align: center;">
            <h1 style="color: white; margin: 0;">HotelMate</h1>
        </div>
        <div style="padding: 30px; background: #f8fafc;">
            <h2 style="color: #1e293b;">Bienvenue sur HotelMate ! 🎉</h2>
            <p style="color: #64748b;">Bonjour <strong>{user_name}</strong>,</p>
            <p style="color: #64748b;">
                Votre compte a été créé avec succès. Vous pouvez maintenant
                découvrir et réserver des billets pour les meilleurs événements.
            </p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="http://localhost:3000"
                    style="background: #4f46e5; color: white; padding: 14px 28px;
                    border-radius: 8px; text-decoration: none; font-weight: bold;">
                    Découvrir les événements
                </a>
            </div>
            <p style="color: #64748b;">L'équipe HotelMate</p>
        </div>
    </div>
    """
    return send_email(user_email, 'Bienvenue sur HotelMate !', html)


def send_password_reset_email(user_email: str, user_name: str, token: str):
    """Email de réinitialisation de mot de passe."""
    reset_link = f"http://localhost:3000/reset-password?token={token}"
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: #4f46e5; padding: 30px; text-align: center;">
            <h1 style="color: white; margin: 0;">HotelMate</h1>
        </div>
        <div style="padding: 30px; background: #f8fafc;">
            <h2 style="color: #1e293b;">Réinitialisation du mot de passe</h2>
            <p style="color: #64748b;">Bonjour <strong>{user_name}</strong>,</p>
            <p style="color: #64748b;">
                Vous avez demandé une réinitialisation de votre mot de passe.
                Cliquez sur le bouton ci-dessous pour continuer.
            </p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_link}"
                    style="background: #4f46e5; color: white; padding: 14px 28px;
                    border-radius: 8px; text-decoration: none; font-weight: bold;">
                    Réinitialiser mon mot de passe
                </a>
            </div>
            <p style="color: #94a3b8; font-size: 12px;">
                Ce lien expire dans 24 heures. Si vous n'avez pas fait cette demande, ignorez cet email.
            </p>
        </div>
    </div>
    """
    return send_email(user_email, 'Réinitialisation de votre mot de passe', html)