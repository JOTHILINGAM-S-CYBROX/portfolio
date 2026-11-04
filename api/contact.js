const nodemailer = require('nodemailer');

module.exports = async function handler(req, res) {
  // Only allow POST requests
  if (req.method !== 'POST') {
    res.setHeader('Allow', ['POST']);
    return res.status(405).json({
      success: false,
      message: `Method ${req.method} not allowed. Please use POST.`
    });
  }

  try {
    const { name, email, subject, message } = req.body || {};

    // Validate required fields
    if (!name || !email || !message) {
      return res.status(400).json({
        success: false,
        message: 'Name, email, and message are required fields.'
      });
    }

    // Basic email format check
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return res.status(400).json({
        success: false,
        message: 'Please provide a valid email address.'
      });
    }

    const gmailUser = process.env.GMAIL_USER || 'jothilingamsivalingamg@gmail.com';
    const gmailAppPassword = process.env.GMAIL_APP_PASSWORD;

    if (!gmailAppPassword) {
      console.error('Missing GMAIL_APP_PASSWORD in environment variables.');
      return res.status(500).json({
        success: false,
        message: 'Email service is unconfigured. Please add GMAIL_APP_PASSWORD in .env'
      });
    }

    // Configure Nodemailer transporter with Gmail SMTP
    const transporter = nodemailer.createTransport({
      service: 'gmail',
      auth: {
        user: gmailUser,
        pass: gmailAppPassword.replace(/\s+/g, '') // remove spaces from app password
      }
    });

    const cleanSubject = subject && subject.trim().length > 0 ? subject.trim() : 'Project Inquiry';
    const timestamp = new Date().toLocaleString('en-US', {
      timeZone: 'Asia/Kolkata',
      dateStyle: 'medium',
      timeStyle: 'short'
    });

    // ========================================================
    // 1. ADMIN NOTIFICATION EMAIL (Delivered to Jothilingam)
    // ========================================================
    const adminSubject = `[Portfolio Lead] ${cleanSubject} — ${name.trim()}`;
    const adminHtml = createAdminEmailTemplate({
      name: name.trim(),
      email: email.trim(),
      subject: cleanSubject,
      message: message.trim(),
      timestamp
    });
    const adminText = `New Message from Portfolio:\nFrom: ${name} (${email})\nSubject: ${cleanSubject}\nDate: ${timestamp} IST\n\nMessage:\n${message}\n\nReply directly to: ${email}`;

    // ========================================================
    // 2. SENDER CONFIRMATION EMAIL (Delivered to Visitor)
    // ========================================================
    const confirmationSubject = `Thank you for reaching out, ${name.trim()} | Jothilingam S`;
    const confirmationHtml = createConfirmationEmailTemplate({
      name: name.trim(),
      email: email.trim(),
      subject: cleanSubject,
      message: message.trim(),
      timestamp
    });
    const confirmationText = `Hi ${name},\n\nThank you for reaching out through my portfolio. I have received your message regarding "${cleanSubject}" and will review it shortly.\n\nSummary of your message:\n${message}\n\nBest regards,\nJothilingam S\nFull-Stack & Cloud Professional\nCoimbatore, Tamil Nadu, India\nEmail: jothilingamsivalingamg@gmail.com\nPhone: +91 89400 66871`;

    // Send Admin Email
    const adminMailPromise = transporter.sendMail({
      from: `"Jothilingam Portfolio" <${gmailUser}>`,
      to: gmailUser,
      replyTo: `"${name}" <${email}>`,
      subject: adminSubject,
      text: adminText,
      html: adminHtml
    });

    // Send Confirmation Email to the Visitor
    const confirmationMailPromise = transporter.sendMail({
      from: `"Jothilingam S" <${gmailUser}>`,
      to: email.trim(),
      replyTo: `"${gmailUser}" <${gmailUser}>`,
      subject: confirmationSubject,
      text: confirmationText,
      html: confirmationHtml
    });

    // Execute both in parallel
    const [adminResult, confirmationResult] = await Promise.allSettled([
      adminMailPromise,
      confirmationMailPromise
    ]);

    if (adminResult.status === 'rejected') {
      console.error('Failed to deliver Admin notification:', adminResult.reason);
      throw adminResult.reason;
    }

    if (confirmationResult.status === 'rejected') {
      console.warn('Could not send confirmation copy to visitor:', confirmationResult.reason);
    }

    return res.status(200).json({
      success: true,
      message: 'Message delivered successfully! A confirmation email has been sent to your inbox.'
    });

  } catch (error) {
    console.error('Error in /api/contact:', error);
    return res.status(500).json({
      success: false,
      message: error.message || 'Failed to send email. Please check your GMAIL_APP_PASSWORD.'
    });
  }
};

// ========================================================
// THEMED HTML TEMPLATES (Editorial Palette: #F4F5F0, #263746, #496D65, #C1A66B)
// ========================================================

function createAdminEmailTemplate({ name, email, subject, message, timestamp }) {
  return `
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
    <body style="margin: 0; padding: 0; background-color: #F4F5F0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
      <div style="background-color: #F4F5F0; padding: 32px 16px;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #FFFFFF; border: 1px solid #DDE2D9; border-radius: 12px; overflow: hidden; box-shadow: 0 8px 24px rgba(38, 55, 70, 0.06);">
          
          <!-- Editorial Header -->
          <div style="background-color: #263746; padding: 28px 28px 24px; border-bottom: 3px solid #C1A66B;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
              <span style="font-size: 11px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; color: #C1A66B;">
                PORTFOLIO LEAD · NEW MESSAGE
              </span>
              <span style="font-size: 11px; color: #89918A; font-family: monospace;">
                ${escapeHtml(timestamp)} IST
              </span>
            </div>
            <h1 style="margin: 0; font-size: 22px; font-weight: 600; color: #FFFFFF; line-height: 1.3;">
              New Inquiry from ${escapeHtml(name)}
            </h1>
          </div>

          <!-- Body Content -->
          <div style="padding: 28px;">
            <!-- Metadata Grid -->
            <table style="width: 100%; border-collapse: collapse; margin-bottom: 22px;">
              <tr>
                <td style="padding: 10px 0; font-size: 11px; font-weight: 700; color: #89918A; text-transform: uppercase; letter-spacing: 0.5px; width: 100px; border-bottom: 1px solid #F4F5F0;">Sender:</td>
                <td style="padding: 10px 0; font-size: 14px; font-weight: 600; color: #263746; border-bottom: 1px solid #F4F5F0;">${escapeHtml(name)}</td>
              </tr>
              <tr>
                <td style="padding: 10px 0; font-size: 11px; font-weight: 700; color: #89918A; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid #F4F5F0;">Email:</td>
                <td style="padding: 10px 0; font-size: 14px; font-weight: 600; color: #496D65; border-bottom: 1px solid #F4F5F0;">
                  <a href="mailto:${escapeHtml(email)}" style="color: #496D65; text-decoration: none;">${escapeHtml(email)}</a>
                </td>
              </tr>
              <tr>
                <td style="padding: 10px 0; font-size: 11px; font-weight: 700; color: #89918A; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid #F4F5F0;">Subject:</td>
                <td style="padding: 10px 0; font-size: 14px; font-weight: 600; color: #263746; border-bottom: 1px solid #F4F5F0;">${escapeHtml(subject)}</td>
              </tr>
            </table>

            <!-- Message Card -->
            <div style="padding: 20px; background-color: #EAEDE6; border-radius: 8px; border-left: 4px solid #496D65;">
              <span style="font-size: 11px; font-weight: 700; color: #496D65; text-transform: uppercase; letter-spacing: 0.5px; display: block; margin-bottom: 8px;">
                Message Content:
              </span>
              <p style="margin: 0; font-size: 14px; line-height: 1.6; color: #263746; white-space: pre-wrap;">
${escapeHtml(message)}
              </p>
            </div>

            <!-- Action CTA -->
            <div style="margin-top: 26px; text-align: center;">
              <a href="mailto:${escapeHtml(email)}?subject=Re: ${encodeURIComponent(subject)}" 
                 style="display: inline-block; background-color: #496D65; color: #FFFFFF; font-size: 13px; font-weight: 600; text-decoration: none; padding: 12px 24px; border-radius: 6px; letter-spacing: 0.5px;">
                Reply Directly to ${escapeHtml(name)}
              </a>
            </div>
          </div>

          <!-- Footer -->
          <div style="background-color: #F4F5F0; padding: 16px 28px; text-align: center; font-size: 11px; color: #89918A; border-top: 1px solid #DDE2D9;">
            Jothilingam S · Digital Craftsmanship Portfolio 2026
          </div>

        </div>
      </div>
    </body>
    </html>
  `;
}

function createConfirmationEmailTemplate({ name, email, subject, message, timestamp }) {
  return `
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
    <body style="margin: 0; padding: 0; background-color: #F4F5F0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
      <div style="background-color: #F4F5F0; padding: 32px 16px;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #FFFFFF; border: 1px solid #DDE2D9; border-radius: 12px; overflow: hidden; box-shadow: 0 8px 24px rgba(38, 55, 70, 0.06);">
          
          <!-- Editorial Header -->
          <div style="background-color: #263746; padding: 28px 28px 24px; border-bottom: 3px solid #C1A66B;">
            <div style="margin-bottom: 6px;">
              <span style="font-size: 11px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; color: #C1A66B;">
                CONFIRMATION · JOTHILINGAM S
              </span>
            </div>
            <h1 style="margin: 0; font-size: 22px; font-weight: 600; color: #FFFFFF; line-height: 1.3;">
              Thank you for connecting, ${escapeHtml(name)}
            </h1>
          </div>

          <!-- Body Content -->
          <div style="padding: 28px;">
            <p style="margin: 0 0 16px; font-size: 15px; line-height: 1.6; color: #263746;">
              Hi <strong>${escapeHtml(name)}</strong>,
            </p>
            <p style="margin: 0 0 16px; font-size: 14px; line-height: 1.6; color: #68736C;">
              Thank you for reaching out through my portfolio. I have successfully received your message regarding <strong style="color: #263746;">"${escapeHtml(subject)}"</strong> and will review it promptly. I typically respond within 24 hours.
            </p>

            <!-- Summary of Submission Box -->
            <div style="margin: 22px 0; padding: 20px; background-color: #EAEDE6; border-radius: 8px; border-left: 4px solid #C1A66B;">
              <span style="font-size: 11px; font-weight: 700; color: #263746; text-transform: uppercase; letter-spacing: 0.5px; display: block; margin-bottom: 8px;">
                Summary of your message:
              </span>
              <p style="margin: 0 0 8px; font-size: 13px; color: #496D65; font-weight: 600;">
                <strong>Subject:</strong> ${escapeHtml(subject)}
              </p>
              <p style="margin: 0; font-size: 13px; line-height: 1.6; color: #263746; white-space: pre-wrap;">
${escapeHtml(message)}
              </p>
            </div>

            <!-- Professional Links & Exploration -->
            <div style="margin-top: 24px; padding-top: 20px; border-top: 1px solid #DDE2D9;">
              <p style="margin: 0 0 12px; font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: #89918A;">
                Connect & Explore Works:
              </p>
              <table style="border-collapse: collapse;">
                <tr>
                  <td style="padding-right: 10px;">
                    <a href="https://linkedin.com/in/jothilingam-s" target="_blank" style="display: inline-block; padding: 9px 16px; background-color: #263746; color: #FFFFFF; font-size: 12px; font-weight: 600; text-decoration: none; border-radius: 6px;">LinkedIn Profile</a>
                  </td>
                  <td>
                    <a href="https://github.com/JOTHILINGAM-S-CYBROX" target="_blank" style="display: inline-block; padding: 9px 16px; background-color: #FFFFFF; border: 1px solid #DDE2D9; color: #263746; font-size: 12px; font-weight: 600; text-decoration: none; border-radius: 6px;">GitHub Repositories</a>
                  </td>
                </tr>
              </table>
            </div>

            <!-- Signature -->
            <div style="margin-top: 28px; padding-top: 18px; border-top: 1px solid #DDE2D9;">
              <p style="margin: 0; font-weight: 700; color: #263746; font-size: 14px;">Jothilingam S</p>
              <p style="margin: 2px 0 0; color: #496D65; font-size: 12px; font-weight: 600;">Full-Stack & Cloud Professional</p>
              <p style="margin: 2px 0 0; font-size: 11px; color: #89918A;">Coimbatore, Tamil Nadu, India · +91 89400 66871</p>
              <p style="margin: 2px 0 0; font-size: 11px; color: #89918A;">Email: jothilingamsivalingamg@gmail.com</p>
            </div>
          </div>

          <!-- Footer -->
          <div style="background-color: #F4F5F0; padding: 14px 28px; text-align: center; font-size: 11px; color: #89918A; border-top: 1px solid #DDE2D9;">
            This is an automated confirmation sent from Jothilingam S Portfolio.
          </div>

        </div>
      </div>
    </body>
    </html>
  `;
}

// Helper to escape HTML characters
function escapeHtml(string) {
  if (!string) return '';
  return String(string)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
