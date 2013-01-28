from Acquisition import aq_inner

from plone.directives import form
from plone.portlets.interfaces import IPortletAssignmentSettings, \
    IPortletAssignment
from plone.app.portlets.browser import z3cformhelper

from zope import schema
from zope.component import adapts
from zope.interface import implements
from zope.i18nmessageid import MessageFactory

from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.schema.interfaces import IVocabularyFactory


from z3c.form import field

_ = MessageFactory('plone')


class CssClassesVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        return SimpleVocabulary([SimpleTerm('class1'),
                                 SimpleTerm('class2')])

class IPortletMetadata(form.Schema):
    """ Schema for portlet metadata """

    is_local = schema.Bool(title=_(u"Local portlet"),
                           description=_(u" "),
                           required=False)

    css_class = schema.Choice(title=_(u"CSS class"),
                              description=_(u" "),
                              vocabulary='plone.app.portlets.CssClasses',
                              required=False)

    exclude_search = schema.Bool(title=(u"Exclude from search"),
                                 description=_(u" "),
                                 required=False,
                                 default=True)


class PortletMetadataAdapter(object):
    adapts(IPortletAssignment)
    implements(IPortletMetadata)

    def __init__(self, context):
        # avoid recursion
        self.__dict__['context'] = context

    def __setattr__(self, attr, value):
        settings = IPortletAssignmentSettings(self.context)
        settings[attr] = value

    def __getattr__(self, attr):
        settings = IPortletAssignmentSettings(self.context)
        return settings.get(attr, None)

    # XXX: Can these be removed?
    def __setitem__(self, attr, value):
        self.__setattr__(attr, value)

    def __getitem__(self, attr):
        return self.__getattr__(attr)


class PortletMetadataEditForm(z3cformhelper.EditForm):
    label = u'Edit portlet settings'
    fields = field.Fields(IPortletMetadata)

    def getContent(self):
        return IPortletMetadata(self.context)

#    @button.buttonAndHandler(_(u'Save'), name='save')
#    def handleApply(self, action):
#        data, errors = self.extractData()
#        if errors:
#            self.status = self.formErrorsMessage
#            return
#        self.applyChanges(data)
#        IStatusMessage(self.request).addStatusMessage(_(u"Changes saved"),
#                                                      "info")
#        self.request.response.redirect(self.context.__parent__.absolute_url() +
#                                       '/@@manage-portlets')
#
#    @button.buttonAndHandler(_(u'Cancel'), name='cancel')
#    def handleCancel(self, action):
#        IStatusMessage(self.request).addStatusMessage(_(u"Edit cancelled"),
#                                                      "info")
#        self.request.response.redirect(self.context.__parent__.absolute_url() +
#                                       '/@@manage-portlets')

