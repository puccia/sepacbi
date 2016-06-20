# -*- coding: UTF-8 -*-
"""Contain test classes for the SDD mode Payment class"""

from unittest import TestCase
from datetime import date, datetime
from lxml import etree
from sepacbi import SddFactory
from sepacbi.bank import Bank
from sepacbi.account import Account
from .test_xml_output import canonicalize_xml

# pylint: disable=no-member

class TestXmlOutput(TestCase):
    """
    Test class for the emit_tag() method
    """

    def setUp(self):
        Payment = SddFactory.get_payment()
        Transaction = SddFactory.get_transaction()
        IdHolder = SddFactory.get_id_holder()
        initiator = IdHolder(name='INITIATOR NAME')
        creditor = IdHolder(name='CREDITOR NAME', old_name='OLD CREDITOR NAME',
                            ics='FR00ZZ123456', old_ics='FR00ZZ654321')
        ultimate_creditor = IdHolder(name='ULTIMATE CREDITOR NAME', identifier='ID-TEST',
                                     address=('Addr Line 1', 'Addr Line 2'), country='FR')
        self.payment = Payment(msg_id='MSG-ID-TEST', initiator=initiator,
                               req_id='PMT-ID-TEST', sequence_type='FRST',
                               collection_date='2016-06-20', bic='ABCDEFGH',
                               account='FR2115583793123088059006193',
                               creditor=creditor, ultimate_creditor=ultimate_creditor)
        first_debtor = IdHolder(name='DEBTOR ONE NAME')
        second_debtor = IdHolder(name='DEBTOR TWO NAME')
        ultimate_debtor = IdHolder(name='ULTIMATE DEBTOR NAME')
        self.payment.add_transaction(eeid='EEID-1-TEST', amount='1234.56',
                                     rum='RUM-TEST-1', signature_date='2016-03-01',
                                     debtor=first_debtor, bic='IJKLMNOP',
                                     account='FR6454953003783660511800042')
        self.payment.add_transaction(eeid='EEID-2-TEST', amount='789.10',
                                     rum='RUM-TEST-2', signature_date='2016-04-01',
                                     old_rum='RUM-TEST-3', debtor=second_debtor,
                                     account='FR8837788964072660207500037',
                                     old_account='FR4448564208620571245246845',
                                     bic='QRSTUVWX', old_bic='YZFEDCBA',
                                     ultimate_debtor=ultimate_debtor)


    def test_xml_text(self):
        """
        Check that the the xml output for the payment is valid.
        msg_id, req_id, collection_date, initiator
        and ultimate_creditor provided.
        Ultimate_debtor and mandate amendment (old_rum, old_bic and old account)
        also provided.
        """
        valid_tag = b'<Document xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="urn:iso:std:iso:20022:tech:xsd:pain.008.001.02">' +\
                     b'<CstmrDrctDbtInitn>' +\
                      b'<GrpHdr>' +\
                       b'<MsgId>MSG-ID-TEST</MsgId>' +\
                       b'<CreDtTm>2016-06-17T09:52:52.358529</CreDtTm>' +\
                       b'<NbOfTxs>2</NbOfTxs>' +\
                       b'<CtrlSum>2023.66</CtrlSum>' +\
                       b'<InitgPty>' +\
                        b'<Nm>INITIATOR NAME</Nm>' +\
                       b'</InitgPty>' +\
                      b'</GrpHdr>' +\
                      b'<PmtInf>' +\
                       b'<PmtInfId>PMT-ID-TEST</PmtInfId>' +\
                       b'<PmtMtd>DD</PmtMtd>' +\
                       b'<PmtTpInf>' +\
                        b'<SvcLvl>' +\
                         b'<Cd>SEPA</Cd>' +\
                        b'</SvcLvl>' +\
                        b'<LclInstrm>' +\
                         b'<Cd>CORE</Cd>' +\
                        b'</LclInstrm>' +\
                        b'<SeqTp>FRST</SeqTp>' +\
                       b'</PmtTpInf>' +\
                       b'<ReqdColltnDt>2016-06-20</ReqdColltnDt>' +\
                       b'<Cdtr>' +\
                        b'<Nm>CREDITOR NAME</Nm>' +\
                       b'</Cdtr>' +\
                       b'<CdtrAcct>' +\
                        b'<Id>' +\
                         b'<IBAN>FR2115583793123088059006193</IBAN>' +\
                        b'</Id>' +\
                       b'</CdtrAcct>' +\
                       b'<CdtrAgt>' +\
                        b'<FinInstnId>' +\
                         b'<BIC>ABCDEFGH</BIC>' +\
                        b'</FinInstnId>' +\
                       b'</CdtrAgt>' +\
                       b'<UltmtCdtr>' +\
                        b'<Nm>ULTIMATE CREDITOR NAME</Nm>' +\
                        b'<PstlAdr>' +\
                         b'<AdrLine>Addr Line 1</AdrLine>' +\
                         b'<AdrLine>Addr Line 2</AdrLine>' +\
                        b'</PstlAdr>' +\
                        b'<Id>' +\
                         b'<OrgId>' +\
                          b'<Othr>' +\
                           b'<Id>ID-TEST</Id>' +\
                          b'</Othr>' +\
                         b'</OrgId>' +\
                        b'</Id>' +\
                        b'<CtryOfRes>FR</CtryOfRes>' +\
                       b'</UltmtCdtr>' +\
                       b'<ChrgBr>SLEV</ChrgBr>' +\
                       b'<CdtrSchmeId>' +\
                        b'<Id>' +\
                         b'<PrvtId>' +\
                          b'<Othr>' +\
                           b'<Id>FR00ZZ123456</Id>' +\
                           b'<SchmeNm>' +\
                            b'<Prtry>SEPA</Prtry>' +\
                           b'</SchmeNm>' +\
                          b'</Othr>' +\
                         b'</PrvtId>' +\
                        b'</Id>' +\
                       b'</CdtrSchmeId>' +\
                       b'<DrctDbtTxInf>' +\
                        b'<PmtId>' +\
                         b'<EndToEndId>EEID-1-TEST</EndToEndId>' +\
                        b'</PmtId>' +\
                        b'<InstdAmt Ccy="EUR">1234.56</InstdAmt>' +\
                        b'<DrctDbtTx>' +\
                         b'<MndtRltdInf>' +\
                          b'<MndtId>RUM-TEST-1</MndtId>' +\
                          b'<DtOfSgntr>2016-03-01</DtOfSgntr>' +\
                          b'<AmdmntInd>true</AmdmntInd>' +\
                          b'<AmdmntInfDtls>' +\
                           b'<OrgnlCdtrSchmeId>' +\
                            b'<Nm>OLD CREDITOR NAME</Nm>' +\
                            b'<Id>' +\
                             b'<PrvtId>' +\
                              b'<Othr>' +\
                               b'<Id>FR00ZZ654321</Id>' +\
                               b'<SchmeNm>' +\
                                b'<Prtry>SEPA</Prtry>' +\
                               b'</SchmeNm>' +\
                              b'</Othr>' +\
                             b'</PrvtId>' +\
                            b'</Id>' +\
                           b'</OrgnlCdtrSchmeId>' +\
                          b'</AmdmntInfDtls>' +\
                         b'</MndtRltdInf>' +\
                        b'</DrctDbtTx>' +\
                        b'<DbtrAgt>' +\
                         b'<FinInstnId>' +\
                          b'<BIC>IJKLMNOP</BIC>' +\
                         b'</FinInstnId>' +\
                        b'</DbtrAgt>' +\
                        b'<Dbtr>' +\
                         b'<Nm>DEBTOR ONE NAME</Nm>' +\
                        b'</Dbtr>' +\
                        b'<DbtrAcct>' +\
                         b'<Id>' +\
                          b'<IBAN>FR6454953003783660511800042</IBAN>' +\
                         b'</Id>' +\
                        b'</DbtrAcct>' +\
                       b'</DrctDbtTxInf>' +\
                       b'<DrctDbtTxInf>' +\
                        b'<PmtId>' +\
                         b'<EndToEndId>EEID-2-TEST</EndToEndId>' +\
                        b'</PmtId>' +\
                        b'<InstdAmt Ccy="EUR">789.10</InstdAmt>' +\
                        b'<DrctDbtTx>' +\
                         b'<MndtRltdInf>' +\
                          b'<MndtId>RUM-TEST-2</MndtId>' +\
                          b'<DtOfSgntr>2016-04-01</DtOfSgntr>' +\
                          b'<AmdmntInd>true</AmdmntInd>' +\
                          b'<AmdmntInfDtls>' +\
                           b'<OrgnlMndtId>RUM-TEST-3</OrgnlMndtId>' +\
                           b'<OrgnlCdtrSchmeId>' +\
                            b'<Nm>OLD CREDITOR NAME</Nm>' +\
                            b'<Id>' +\
                             b'<PrvtId>' +\
                              b'<Othr>' +\
                               b'<Id>FR00ZZ654321</Id>' +\
                               b'<SchmeNm>' +\
                                b'<Prtry>SEPA</Prtry>' +\
                               b'</SchmeNm>' +\
                              b'</Othr>' +\
                             b'</PrvtId>' +\
                            b'</Id>' +\
                           b'</OrgnlCdtrSchmeId>' +\
                           b'<OrgnlDbtrAcct>' +\
                            b'<Id>' +\
                             b'<IBAN>FR4448564208620571245246845</IBAN>' +\
                            b'</Id>' +\
                           b'</OrgnlDbtrAcct>' +\
                           b'<OrgnlDbtrAgt>' +\
                            b'<FinInstnId>' +\
                             b'<Othr>' +\
                              b'<Id>YZFEDCBA</Id>' +\
                             b'</Othr>' +\
                            b'</FinInstnId>' +\
                           b'</OrgnlDbtrAgt>' +\
                          b'</AmdmntInfDtls>' +\
                         b'</MndtRltdInf>' +\
                        b'</DrctDbtTx>' +\
                        b'<DbtrAgt>' +\
                         b'<FinInstnId>' +\
                          b'<BIC>QRSTUVWX</BIC>' +\
                         b'</FinInstnId>' +\
                        b'</DbtrAgt>' +\
                        b'<Dbtr>' +\
                         b'<Nm>DEBTOR TWO NAME</Nm>' +\
                        b'</Dbtr>' +\
                        b'<DbtrAcct>' +\
                         b'<Id>' +\
                          b'<IBAN>FR8837788964072660207500037</IBAN>' +\
                         b'</Id>' +\
                        b'</DbtrAcct>' +\
                        b'<UltmtDbtr>' +\
                         b'<Nm>ULTIMATE DEBTOR NAME</Nm>' +\
                        b'</UltmtDbtr>' +\
                       b'</DrctDbtTxInf>' +\
                      b'</PmtInf>' +\
                     b'</CstmrDrctDbtInitn>' +\
                    b'</Document>'
        to_check_tag = self.payment.xml_text()
        self.assertEqual(canonicalize_xml(valid_tag), canonicalize_xml(to_check_tag))

    def test_xml_text(self):
        """
        Check that the the xml output for the payment is valid.
        msg_id, req_id, collection_date, initiator
        and ultimate_creditor not provided.
        Ultimate_debtor and mandate amendment (old_rum, old_bic and old account)
        also provided.
        """
        valid_tag = b'<Document xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="urn:iso:std:iso:20022:tech:xsd:pain.008.001.02">' +\
                     b'<CstmrDrctDbtInitn>' +\
                      b'<GrpHdr>' +\
                       b'<MsgId>DistintaXml-20160620-172835</MsgId>' +\
                       b'<CreDtTm>2016-06-17T09:52:52.358529</CreDtTm>' +\
                       b'<NbOfTxs>2</NbOfTxs>' +\
                       b'<CtrlSum>2023.66</CtrlSum>' +\
                       b'<InitgPty>' +\
                        b'<Nm>INITIATOR NAME</Nm>' +\
                       b'</InitgPty>' +\
                      b'</GrpHdr>' +\
                      b'<PmtInf>' +\
                       b'<PmtInfId>PMT-ID-TEST</PmtInfId>' +\
                       b'<PmtMtd>DD</PmtMtd>' +\
                       b'<PmtTpInf>' +\
                        b'<SvcLvl>' +\
                         b'<Cd>SEPA</Cd>' +\
                        b'</SvcLvl>' +\
                        b'<LclInstrm>' +\
                         b'<Cd>CORE</Cd>' +\
                        b'</LclInstrm>' +\
                        b'<SeqTp>FRST</SeqTp>' +\
                       b'</PmtTpInf>' +\
                       b'<ReqdColltnDt>2016-06-20</ReqdColltnDt>' +\
                       b'<Cdtr>' +\
                        b'<Nm>CREDITOR NAME</Nm>' +\
                       b'</Cdtr>' +\
                       b'<CdtrAcct>' +\
                        b'<Id>' +\
                         b'<IBAN>FR2115583793123088059006193</IBAN>' +\
                        b'</Id>' +\
                       b'</CdtrAcct>' +\
                       b'<CdtrAgt>' +\
                        b'<FinInstnId>' +\
                         b'<BIC>ABCDEFGH</BIC>' +\
                        b'</FinInstnId>' +\
                       b'</CdtrAgt>' +\
                       b'<UltmtCdtr>' +\
                        b'<Nm>ULTIMATE CREDITOR NAME</Nm>' +\
                        b'<PstlAdr>' +\
                         b'<AdrLine>Addr Line 1</AdrLine>' +\
                         b'<AdrLine>Addr Line 2</AdrLine>' +\
                        b'</PstlAdr>' +\
                        b'<Id>' +\
                         b'<OrgId>' +\
                          b'<Othr>' +\
                           b'<Id>ID-TEST</Id>' +\
                          b'</Othr>' +\
                         b'</OrgId>' +\
                        b'</Id>' +\
                        b'<CtryOfRes>FR</CtryOfRes>' +\
                       b'</UltmtCdtr>' +\
                       b'<ChrgBr>SLEV</ChrgBr>' +\
                       b'<CdtrSchmeId>' +\
                        b'<Id>' +\
                         b'<PrvtId>' +\
                          b'<Othr>' +\
                           b'<Id>FR00ZZ123456</Id>' +\
                           b'<SchmeNm>' +\
                            b'<Prtry>SEPA</Prtry>' +\
                           b'</SchmeNm>' +\
                          b'</Othr>' +\
                         b'</PrvtId>' +\
                        b'</Id>' +\
                       b'</CdtrSchmeId>' +\
                       b'<DrctDbtTxInf>' +\
                        b'<PmtId>' +\
                         b'<EndToEndId>EEID-1-TEST</EndToEndId>' +\
                        b'</PmtId>' +\
                        b'<InstdAmt Ccy="EUR">1234.56</InstdAmt>' +\
                        b'<DrctDbtTx>' +\
                         b'<MndtRltdInf>' +\
                          b'<MndtId>RUM-TEST-1</MndtId>' +\
                          b'<DtOfSgntr>2016-03-01</DtOfSgntr>' +\
                          b'<AmdmntInd>true</AmdmntInd>' +\
                          b'<AmdmntInfDtls>' +\
                           b'<OrgnlCdtrSchmeId>' +\
                            b'<Nm>OLD CREDITOR NAME</Nm>' +\
                            b'<Id>' +\
                             b'<PrvtId>' +\
                              b'<Othr>' +\
                               b'<Id>FR00ZZ654321</Id>' +\
                               b'<SchmeNm>' +\
                                b'<Prtry>SEPA</Prtry>' +\
                               b'</SchmeNm>' +\
                              b'</Othr>' +\
                             b'</PrvtId>' +\
                            b'</Id>' +\
                           b'</OrgnlCdtrSchmeId>' +\
                          b'</AmdmntInfDtls>' +\
                         b'</MndtRltdInf>' +\
                        b'</DrctDbtTx>' +\
                        b'<DbtrAgt>' +\
                         b'<FinInstnId>' +\
                          b'<BIC>IJKLMNOP</BIC>' +\
                         b'</FinInstnId>' +\
                        b'</DbtrAgt>' +\
                        b'<Dbtr>' +\
                         b'<Nm>DEBTOR ONE NAME</Nm>' +\
                        b'</Dbtr>' +\
                        b'<DbtrAcct>' +\
                         b'<Id>' +\
                          b'<IBAN>FR6454953003783660511800042</IBAN>' +\
                         b'</Id>' +\
                        b'</DbtrAcct>' +\
                       b'</DrctDbtTxInf>' +\
                       b'<DrctDbtTxInf>' +\
                        b'<PmtId>' +\
                         b'<EndToEndId>EEID-2-TEST</EndToEndId>' +\
                        b'</PmtId>' +\
                        b'<InstdAmt Ccy="EUR">789.10</InstdAmt>' +\
                        b'<DrctDbtTx>' +\
                         b'<MndtRltdInf>' +\
                          b'<MndtId>RUM-TEST-2</MndtId>' +\
                          b'<DtOfSgntr>2016-04-01</DtOfSgntr>' +\
                          b'<AmdmntInd>true</AmdmntInd>' +\
                          b'<AmdmntInfDtls>' +\
                           b'<OrgnlMndtId>RUM-TEST-3</OrgnlMndtId>' +\
                           b'<OrgnlCdtrSchmeId>' +\
                            b'<Nm>OLD CREDITOR NAME</Nm>' +\
                            b'<Id>' +\
                             b'<PrvtId>' +\
                              b'<Othr>' +\
                               b'<Id>FR00ZZ654321</Id>' +\
                               b'<SchmeNm>' +\
                                b'<Prtry>SEPA</Prtry>' +\
                               b'</SchmeNm>' +\
                              b'</Othr>' +\
                             b'</PrvtId>' +\
                            b'</Id>' +\
                           b'</OrgnlCdtrSchmeId>' +\
                           b'<OrgnlDbtrAcct>' +\
                            b'<Id>' +\
                             b'<IBAN>FR4448564208620571245246845</IBAN>' +\
                            b'</Id>' +\
                           b'</OrgnlDbtrAcct>' +\
                           b'<OrgnlDbtrAgt>' +\
                            b'<FinInstnId>' +\
                             b'<Othr>' +\
                              b'<Id>YZFEDCBA</Id>' +\
                             b'</Othr>' +\
                            b'</FinInstnId>' +\
                           b'</OrgnlDbtrAgt>' +\
                          b'</AmdmntInfDtls>' +\
                         b'</MndtRltdInf>' +\
                        b'</DrctDbtTx>' +\
                        b'<DbtrAgt>' +\
                         b'<FinInstnId>' +\
                          b'<BIC>QRSTUVWX</BIC>' +\
                         b'</FinInstnId>' +\
                        b'</DbtrAgt>' +\
                        b'<Dbtr>' +\
                         b'<Nm>DEBTOR TWO NAME</Nm>' +\
                        b'</Dbtr>' +\
                        b'<DbtrAcct>' +\
                         b'<Id>' +\
                          b'<IBAN>FR8837788964072660207500037</IBAN>' +\
                         b'</Id>' +\
                        b'</DbtrAcct>' +\
                        b'<UltmtDbtr>' +\
                         b'<Nm>ULTIMATE DEBTOR NAME</Nm>' +\
                        b'</UltmtDbtr>' +\
                       b'</DrctDbtTxInf>' +\
                      b'</PmtInf>' +\
                     b'</CstmrDrctDbtInitn>' +\
                    b'</Document>'
        to_delete_attr = ('msg_id', 'initiator', 'req_id',
                          'collection_date', 'ultimate_creditor')
        list([delattr(self.payment, attr) for attr in to_delete_attr])
        to_check_tag = self.payment.xml_text()
        self.assertEqual(canonicalize_xml(valid_tag, mode='gen_id'), canonicalize_xml(to_check_tag, mode='gen_id'))
