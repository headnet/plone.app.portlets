from Acquisition import aq_inner

from plone.directives import form
from plone.portlets.interfaces import IPortletAssignmentSettings, \
    IPortletAssignmentMapping
from plone.app.z3cform import layout

from Products.statusmessages.interfaces import IStatusMessage

from zope import schema
from zope.component import adapts
from zope.interface import implements
from zope.i18nmessageid import MessageFactory

from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.schema.interfaces import IVocabularyFactory


from z3c.form import button, field, interfaces

_ = MessageFactory('plone')


class CssClassesVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        return SimpleVocabulary([SimpleTerm('class1'),
                                 SimpleTerm('class2')])


class IPortletMetadata(form.Schema):
    """ Schema for portlet metadata """

    name = schema.TextLine(title=_(u"Name"),
                           required=False)

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
    adapts(IPortletAssignmentMapping)
    implements(IPortletMetadata)

    def __init__(self, context):
        self.__dict__['context'] = context

    @property
    def name(self):
        return self.context.REQUEST.get('form.widgets.name')

    def __setattr__(self, attr, value):
        if self.name is None:
            return

        assignments = aq_inner(self.context)
        settings = IPortletAssignmentSettings(assignments[self.name])
        settings[attr] = value

    def __getattr__(self, attr):
        if self.name is None:
            return None

        assignments = aq_inner(self.context)
        settings = IPortletAssignmentSettings(assignments[self.name])
        return settings.get(attr, None)

    # XXX: Can these be removed?
    def __setitem__(self, attr, value):
        self.__setattr__(attr, value)

    def __getitem__(self, attr):
        return self.__getattr__(attr)


class PortletMetadataEditForm(form.EditForm):

    label = u'Portlet metadata form'
    fields = field.Fields(IPortletMetadata)

    ignoreContext = False

    def updateWidgets(self):
        super(PortletMetadataEditForm, self).updateWidgets()
        self.widgets['name'].mode = interfaces.HIDDEN_MODE

    def getContent(self):
        return IPortletMetadata(self.context)

    @button.buttonAndHandler(_(u'Save'), name='save')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        self.applyChanges(data)
        IStatusMessage(self.request).addStatusMessage(_(u"Changes saved"),
                                                      "info")
        self.request.response.redirect(self.context.__parent__.absolute_url() +
                                       '/@@manage-portlets')

    @button.buttonAndHandler(_(u'Cancel'), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(_(u"Edit cancelled"),
                                                      "info")
        self.request.response.redirect(self.context.__parent__.absolute_url() +
                                       '/@@manage-portlets')


PortletMetadataFormView = layout.wrap_form(PortletMetadataEditForm,
                                           label="Metadata Edit Form")
