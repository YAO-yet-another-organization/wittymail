#!/usr/bin/env python
# coding=utf-8

import os, sys
sys.path.append(os.path.abspath(os.path.join(os.curdir, '..', '..')))

import mailer.emailapi_broker as emailapi_broker
from wittymail_server import flask_app
from flask import jsonify, request, json
import util.version as version
import util.logger as logger

log = logger.get_logger(__name__)

HTTP_OK         = 200
HTTP_CREATED    = 201
HTTP_NOT_FOUND  = 404
HTTP_BAD_INPUT  = 400

@flask_app.route("/api/version", methods=['GET'])
def get_version():
    log.debug('Current version = %s' % (version.__pretty_version__))
    return (jsonify({'version': version.__pretty_version__}),
              HTTP_OK,
              {'ContentType':'application/json'})
    
@flask_app.route("/api/fodder/regurgitate", methods=['GET'])
def get_fodder_regurgitate():
    fodder_names = emailapi_broker.get_email_fodder_names()
    fodder = emailapi_broker.get_email_fodder()

    if len(fodder_names) == 0 or len(fodder) == 0:    
        return "Data sheet is empty or data sheet is not provided", HTTP_NOT_FOUND

    cnt = 0
    fodder_list = []
    for f in fodder:
        if cnt == 2:
          break
        fodder_list.append(dict(zip(fodder_names, f)))
        cnt += 1

    if cnt == 0:
        return (jsonify({'error_message': "Data sheet is empty or data sheet is not provided"}),
            HTTP_NOT_FOUND,
            {'ContentType':'application/json'})

    return (jsonify({'headers': fodder_names, 'contents': fodder_list}),
              HTTP_OK,
              {'ContentType':'application/json'})

  

@flask_app.route("/api/fodder", methods=['POST'])
def post_fodder():
    log.info(request.files)
    try:
        fodder_dir = emailapi_broker.get_fodder_dir()

        f = request.files['fodder']
        fodder_file = os.path.join(fodder_dir, f.filename)
        f.save(fodder_file)
        log.info('fodder file saved as = %s' % (fodder_file))

        emailapi_broker.save_fodder_from_file(fodder_file)
    except:
        log.exception("Message")
    return (jsonify({}),
            HTTP_OK,
            {'ContentType':'application/json'})


# TODO Change this to a get request because using post for get is, well, stupid
# Check how to send multi line data in GET request 
@flask_app.route("/api/email/template", methods=['POST'])
def get_email_template():
    data = json.loads(request.data)
    fodder = emailapi_broker.get_email_fodder() 
    result_str = emailapi_broker.template_to_str(data['template'], fodder[0])

    return (jsonify({'reality': result_str}), 
              HTTP_OK,
                {'ContentType':'application/json'})

@flask_app.route("/api/fodder/ingredients", methods=['GET'])
def get_fodder_ingredients():
    fodder_names = emailapi_broker.get_email_fodder_names()
    if len(fodder_names) == 0:
           return (jsonify({'error_message': "Data sheet is empty or data sheet is not provided"}),
                  HTTP_NOT_FOUND,
                  {'ContentType':'application/json'})

    return (jsonify(fodder_names),
            HTTP_OK,
            {'ContentType':'application/json'})

@flask_app.route("/api/attachment/mapping", methods=['POST'])
def post_attachment_mapping():
    data = json.loads(request.data)
    emailapi_broker.save_attachment_column(data['attachment_column'])
    return (jsonify({}),
            HTTP_OK,
            {'ContentType':'application/json'})


@flask_app.route("/api/attachment/validate", methods=['GET'])
def get_attachment_validate():
  fodder_names = emailapi_broker.get_email_fodder_names()
  fodder = emailapi_broker.get_email_fodder()

  if len(fodder_names) == 0 or len(fodder) == 0:    
    return (jsonify({'error_message': "Data sheet is empty or data sheet is not provided"}),
            HTTP_NOT_FOUND,
            {'ContentType':'application/json'})

  issue_index = fodder_names.index("status")

  fodder_list = []
  for f in fodder:
      if f[issue_index] != "All is well":
        fodder_list.append(dict(zip(fodder_names, f)))

  return (jsonify({'headers': fodder_names, 'content': fodder_list}),
            HTTP_OK,
            {'ContentType':'application/json'})

@flask_app.route("/api/attachment", methods=['POST'])
def post_attachment():
    '''
    The 3rd party Angular plugin ng6-file-upload makes one POST call per file instead of 
    sending them all at once.
    
    To workaround this stupitidy, this API is idempotent and will just keep saving
    all files in the same dir
    '''
    try:
        a = request.files['attachment']
        attachment_dir = emailapi_broker.get_attachments_dir()
    
        a.save(os.path.join(attachment_dir, a.filename))
        log.info('Attachment file saved as = %s' % (attachment_dir + a.filename))
    
        emailapi_broker.save_attachment_dir(attachment_dir)
        return "Attachments saved successfully", HTTP_OK
    except:
        log.exception("")

@flask_app.route("/api/email", methods=['POST'])
def post_email():
    data = json.loads(request.data)
    if data['to_column'] == None or data['cc_column'] == None or data['subject_template'] == None or data['body_template'] == None:
        return (jsonify({'error_message': "to, cc, subject or body not provided"}),
              HTTP_NOT_FOUND,
              {'ContentType':'application/json'})

    emailapi_broker.save_extended_fodder(data['to_column'], data['cc_column'], data['subject_template'], data['body_template']) 
    return (jsonify({}),
        HTTP_OK,
        {'ContentType':'application/json'})


@flask_app.route("/api/email/test", methods=['POST'])
def post_email_test():
    data = json.loads(request.data)
    tos = []
    tos.append(data['to'])
    e = emailapi_broker.send_email(tos)
    if e[0] is not 0:
        return e[1], HTTP_NOT_FOUND
    return (jsonify({}),
              HTTP_OK,
              {'ContentType':'application/json'})

@flask_app.route("/api/email/send", methods=['POST'])
def post_email_send():
    data = json.loads(request.data)
    e = emailapi_broker.send_email()
    if e[0] is not 0:
        return e[1], HTTP_NOT_FOUND
    return (jsonify({}),
              HTTP_OK,
              {'ContentType':'application/json'})


@flask_app.route("/api/vomit", methods=['GET'])
def get_vomit():
    fodder_names = emailapi_broker.get_email_fodder_names()

    fodder = emailapi_broker.get_email_fodder()
    extended_fodder = emailapi_broker.get_extended_email_fodder()

    if len(fodder_names) == 0 or len(fodder) == 0 or len(extended_fodder) == 0:    
        return (jsonify({'error_message': "Data sheet or email template not provided"}),
              HTTP_NOT_FOUND,
              {'ContentType':'application/json'})

    assert len(fodder) == len(extended_fodder), "Count of fodder and extended_fodder do not match"    

    if emailapi_broker.EMAIL_FODDER_TO_INDEX == None or emailapi_broker.EMAIL_FODDER_CC_INDEX == None:
        return (jsonify({'error_message': "'To' or 'CC' index not provided"}),
              HTTP_NOT_FOUND,
              {'ContentType':'application/json'})

    fodder_list = []
    for f, e in zip(fodder, extended_fodder):
        email = { \
          "from": emailapi_broker.email_from,
          "to": f[emailapi_broker.EMAIL_FODDER_TO_INDEX],
          "cc": f[emailapi_broker.EMAIL_FODDER_CC_INDEX],
          "attachment": {"name": e[-2][0], "url": os.path.join("/api/attachment/", e[-2][0]) if e[-2] else "Not found"},
          "subject": e[-4],
          "body": e[-3],
        }

        tmp = dict(zip(fodder_names, f))
        tmp["email"] = email
        fodder_list.append(tmp)

    return (jsonify({'headers': fodder_names, 'contents': fodder_list}),
              HTTP_OK,
              {'ContentType':'application/json'})

@flask_app.route("/api/email_server", methods=['POST'])
def post_email_server():
    data = json.loads(request.data)

    assert len(data['username']) > 0 and len(data['password']) > 0, "username or password not provided"

    e = emailapi_broker.set_login_details(data['username'], data['password'])

    if e[0] is not 0:
        return (jsonify({'error_message': e[1]}),
              HTTP_BAD_INPUT,
              {'ContentType':'application/json'})

    return (jsonify({'error_message': ""}),
              HTTP_OK,
              {'ContentType':'application/json'})
