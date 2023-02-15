import oci
from oci.identity.models import CreateApiKeyDetails

class OCIAdmin:
    def __init__(self):
        self.config = oci.config.from_file()
        self.identity = oci.identity.IdentityClient(self.config)
        self.user_email = None
        self.user_ocid = None
        self.upload_api_key_response = None
        self.apiKeyUploaded = True
    
    def list_users_in_tenancy(self):
        return self.identity.list_users(self.config["tenancy"]).data
    
    def get_user_ocid(self):
        users_list = self.list_users_in_tenancy()
        for user in users_list:
            if user.email == self.user_email:
                self.user_ocid = user.id
                break
                
        if self.user_ocid is None:
            print("User with given email id not found!")
            print("Available Users are : ")
            print([i.email for i in users_list])
        else:
            print("OCID of user with given email id is : {}".format(self.user_ocid))
                
    def upload_api_key(self):
        with open("C://Users/dharshans/.oci/oci_api_key_public.pem", "r") as certfile:
            akpub = certfile.read()
        cak = CreateApiKeyDetails(key=akpub)
        try:
            self.upload_api_key_response = self.identity.upload_api_key(self.user_ocid, cak).data
        except oci.exceptions.ServiceError as servErr:
            if "already exists" in servErr.message:
                print("The API Key for user {} already exists".format(self.user_email))
                self.apiKeyUploaded = False
                for apikeys in self.identity.list_api_keys(self.user_ocid).data:
                    if apikeys.fingerprint==self.config["fingerprint"]:
                        self.upload_api_key_response = apikeys
                        break
            else:
                print(servErr)

    def list_compartments(self):
        temp_config = {**self.config}
        temp_config["user"] = self.user_ocid
        temp_identity = oci.identity.IdentityClient(temp_config)
        accsCompRoot = temp_identity.list_compartments(temp_config["tenancy"], access_level="ACCESSIBLE").data
        accsCompSubtree = temp_identity.list_compartments(temp_config["tenancy"], access_level="ACCESSIBLE", compartment_id_in_subtree=True).data
        print([i.name for i in accsCompRoot])
        print([i.name for i in accsCompSubtree])
        
    def delete_api_key(self):
        if self.apiKeyUploaded:
            self.identity.delete_api_key(self.user_ocid, self.upload_api_key_response.fingerprint)
def main():
    oci_admin = OCIAdmin()
    oci_admin.user_email = input("Enter user email: ")
    oci_admin.get_user_ocid()
    if oci_admin.user_ocid is not None:
        oci_admin.upload_api_key()
        oci_admin.list_compartments()
        oci_admin.delete_api_key()

if __name__ == "__main__":
    main()
