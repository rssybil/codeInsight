<script>
import axios from 'axios';

export default {
  methods: {
    // call codeCollaboration API
    async codeCollaboration(userMessage, currentCode) {
      try {
        const response = await axios.post('http://localhost:5000/api/code-collaboration', {
          user_message: userMessage,
          current_code: currentCode
        });
        return response.data;
      } catch (error) {
        console.error('Error in codeCollaboration:', error);
        return { error: error.message };
      }
    },

    // call quickAction API
    async quickAction(action, currentCode) {
      try {
        const response = await axios.post('http://localhost:5000/api/quick-action', {
          action: action,
          current_code: currentCode
        });
        return response.data;
      } catch (error) {
        console.error('Error in quickAction:', error);
        return { error: error.message };
      }
    }
  }
};
</script>
